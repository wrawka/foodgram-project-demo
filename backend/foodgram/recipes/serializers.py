from dataclasses import fields
from rest_framework import serializers

from .models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = '__all__'
