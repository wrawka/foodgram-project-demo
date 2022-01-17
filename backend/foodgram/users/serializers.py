from email.policy import default
from enum import unique
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators, permissions
from .models import Follow


User = get_user_model()


class FoodgramUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators = [
            validators.UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже зарегистрирован.'
            )
        ],
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class FoodgramUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, following):
        result = False
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            result = user.is_authenticated
        if result:
            result = Follow.objects.filter(user=user, following=following).exists()
        return result


class UserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = ...
    recipes_count = ...


class FollowSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, attrs):
        user = attrs['user']
        following = attrs['following']
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError('Already subscribed to this user.')
        if user == following:
            raise serializers.ValidationError('Can\'t follow self.')
        return super().validate(attrs)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return FoodgramUserSerializer(instance=instance.following, context=context)
