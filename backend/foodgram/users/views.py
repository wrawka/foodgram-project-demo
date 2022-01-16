from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowSerializer


User = get_user_model()

class Subscribe(APIView):

    def get_following(self, request, pk):
        return get_object_or_404(User, pk=pk)

    def post(self, request, pk):
        serializer = FollowSerializer(
            Follow.objects.create(user=self.request.user,
                following = self.get_following()
            )
        )
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pass