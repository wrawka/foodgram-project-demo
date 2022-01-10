from django.db import models

class Ingredient(models.Model):
    name = models.CharField()
    measurement_unit = models.CharField()


class Recipe(models.Model):
    name = models.CharField()
    ingredients = ...
    tags = ...
    image = ...
    text = models.TextField()
    cooking_time = ...


