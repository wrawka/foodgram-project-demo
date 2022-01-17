from django.contrib import admin
from .models import Ingredient, Recipe, Tag, RecipeIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass
@admin.register(RecipeIngredient)
class RecipeIngAdmin(admin.ModelAdmin):
    pass
