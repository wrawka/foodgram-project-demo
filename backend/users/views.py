from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from .models import Follow
from .serializers import SubscriptionUserSerializer


User = get_user_model()


class FollowViewSet(GenericViewSet):
    serializer_class = SubscriptionUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['author__username', 'user__username']
    pagination_class = LimitOffsetPagination

    @action(detail=False)
    def subscriptions(self, request):
        following = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = SubscriptionUserSerializer(
                page, context={'request': request}, many=True
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionUserSerializer(
            following, context={'request': request}, many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if author == request.user:
            return Response(
                {'errors': 'Can\'t follow self.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            Follow.objects.create(user=request.user, author=author)
        except IntegrityError:
            return Response(
                {'errors': 'Already subscribed to this user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        try:
            Follow.objects.get(
                user=request.user.id,
                author=author.id
            ).delete()
        except Follow.DoesNotExist:
            return Response(
                {'errors': 'Not following this author.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
