import django_filters.rest_framework as df
from recipes.models import Favourites, ShoppingCart

from django.db.models import IntegerField, Value

from .models import Ingredient, Recipe


class IngredientSearchFilter(df.FilterSet):
    name = df.CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in start_with_queryset)
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')


class RecipeFilter(df.FilterSet):
    is_favorited = df.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = df.BooleanFilter(method='get_is_in_shopping_cart')
    tags = df.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not value or not user.is_authenticated:
            return queryset
        try:
            favorite_recipes = user.favourites.recipes.all()
        except Favourites.DoesNotExist:
            return queryset
        return queryset.filter(
            pk__in=(recipe.pk for recipe in favorite_recipes)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not value or not user.is_authenticated:
            return queryset
        try:
            shopping_cart = user.shoppingcart.recipes.all()
        except ShoppingCart.DoesNotExist:
            return queryset
        return queryset.filter(
            pk__in=(recipe.pk for recipe in shopping_cart)
        )
