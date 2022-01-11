from django.db import models
from django.core.validators import MinValueValidator


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, null=True)
    slug = models.SlugField(null=True)


class Ingredient(models.Model):
    name = models.CharField()
    measurement_unit = models.CharField()

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    image = models.CharField()
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()
