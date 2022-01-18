from dataclasses import fields
from users.serializers import FoodgramUserSerializer
from rest_framework import serializers

from .models import MeasuredIngredient, RecipeIngredients, Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'

    def get_fields(self):
        return super().get_fields()




class IngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredient
        fields = '__all__'


# class RecipeTagSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(Tag.objects.all(), )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=RecipeIngredients.objects.all(), source='ingredient')
    amount = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit','amount']

    def to_representation(self, instance):
        return super().to_representation(instance)
    

class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            recipe_ingredient = MeasuredIngredient.objects.create(
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
        )
            recipe.ingredients.add(recipe_ingredient)
        return recipe

    def to_representation(self, instance):
        return super().to_representation(instance)
