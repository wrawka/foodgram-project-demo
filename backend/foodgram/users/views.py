from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .models import Follow
from .serializers import FollowSerializer, FoodgramUserSerializer


User = get_user_model()

class FollowViewSet(GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['following__username', 'user__username']
    pagination_class=LimitOffsetPagination

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    @action(detail=True)
    def subscribe(self, request, pk):
        following_user = get_object_or_404(User, id=pk)
        serializer = self.get_serializer(data={'user': request.user.id, 'following': following_user.id})
        if serializer.is_valid():
            serializer.save(
                user=self.request.user,
                following=following_user
            )
            some_data = serializer.data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        following_instance = get_object_or_404(
            Follow,
            user=request.user.id, 
            following=get_object_or_404(User, id=pk).id)
        following_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        following = request.user.following.all()
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = FollowSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(following, context={'request': request}, many=True)
        return Response(serializer.data)
