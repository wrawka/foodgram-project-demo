from rest_framework import serializers, validators
from django.db import models


from recipes.models import RecipeIngredients, Tag, Ingredient, Recipe
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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient.id')
    amount = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit','amount']

    def to_representation(self, instance):
        """ Swapping queryset from Ingredient to RecipeIngredient. """
        recipe_ingredient = instance.recipeingredients_set.all().first()
        return super().to_representation(recipe_ingredient)


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        # validators = [
        #     validators.UniqueValidator(
        #         queryset=RecipeIngredients.objects.filter(),
        #         fields=['recipe', 'ingredient']
        #     )
        # ]

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
