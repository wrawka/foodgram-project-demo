from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, null=True, unique=True)
    slug = models.SlugField(unique=True, null=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', null=True)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredients')
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=200)
    image = models.TextField()
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.DO_NOTHING)
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='ingredient_unique_in_recipe'
            ),
        ]

    # def __str__(self) -> str:
    #     return f'{self.ingredient.name} - {self.amount} {self.ingredient.measurement_unit}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)


class Favourites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)
