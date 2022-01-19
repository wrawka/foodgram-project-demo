from users.serializers import FoodgramUserSerializer
from rest_framework import serializers

from .models import RecipeIngredients, Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'

    def to_representation(self, instance):
        return super().to_representation(instance)


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

    def create(self, validated_data):
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

    def to_representation(self, instance):
        tags_ser = TagSerializer(self.instance.tags.all(), many=True)
        rep = super().to_representation(instance)
        rep['tags'] = tags_ser.data
        return rep
