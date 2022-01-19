from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowSerializer


User = get_user_model()

class FollowViewSet(GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['following__username', 'user__username']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_id = self.kwargs.get('id')
        following_user = get_object_or_404(User, id=following_id)
        serializer.save(
            user=self.request.user,
            following=following_user
        )

    @action(detail=True)
    def subscribe(self, request, pk):
        following_user = get_object_or_404(User, id=pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=self.request.user,
                following=following_user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
