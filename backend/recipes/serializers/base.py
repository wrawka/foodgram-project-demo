from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from django.db import models

from recipes.models import (
    Favourites, Ingredient, Recipe, RecipeIngredients, ShoppingCart, Tag
)

from users.serializers import FoodgramUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    amount = serializers.IntegerField(min_value=1)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def to_representation(self, instance):
        """ Swapping queryset from Ingredient to RecipeIngredient. """
        recipe_ingredient = instance.recipeingredients_set.all().first()
        return super().to_representation(recipe_ingredient)


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_user(self):
        return self.context['request'].user

    def create(self, validated_data):
        """ Custom create method to handle nested tags and ingredients. """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        """ Custom update method by overwriting tags and ingredients. """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        recipe.recipeingredients_set.all().delete()
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
        return super().update(recipe, validated_data)

    def to_representation(self, data):
        """ Serializing tags manually. """
        iterable = data.all() if isinstance(data, models.Manager) else data
        tags_ser = TagSerializer(iterable.tags.all(), many=True)
        rep = super().to_representation(iterable)
        rep['tags'] = tags_ser.data
        return rep

    def get_is_favorited(self, recipe):
        user = self.get_user()
        if user.is_authenticated:
            try:
                favourites = user.favourites_set.get().recipes.all()
                return recipe in favourites
            except Favourites.DoesNotExist:
                pass
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.get_user()
        if user.is_authenticated:
            try:
                shopping_cart = user.shoppingcart_set.get().recipes.all()
                return recipe in shopping_cart
            except ShoppingCart.DoesNotExist:
                pass
        return False
