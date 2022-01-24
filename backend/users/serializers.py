from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators

from django.contrib.auth import get_user_model

from recipes.serializers.nested import Recipe, RecipeLiteSerializer

from .models import Follow


User = get_user_model()


class FoodgramUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[
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
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        result = False
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            result = user.is_authenticated
        if result:
            result = Follow.objects.filter(user=user, author=author).exists()
        return result


class SubscriptionUserSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_recipes(self, user):
        queryset = Recipe.objects.filter(author=user)
        limit = queryset.count()
        request = self.context.get('request')
        if request:
            limit = int(request.query_params.get('recipes_limit', limit))
        return RecipeLiteSerializer(queryset[:limit], many=True).data
