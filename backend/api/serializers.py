from rest_framework import serializers
from users.serializers import FoodgramUserSerializer
from recipes.serializers.base import RecipeSerializer


class UserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'

    def get_recipes_count(self, obj):
        pass