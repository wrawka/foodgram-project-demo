from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .filters import IngredientSearchFilter, RecipeFilter
from .models import Favourites, Ingredient, Recipe, ShoppingCart, Tag
from .serializers.base import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)
from .serializers.nested import RecipeLiteSerializer


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientSearchFilter


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, name="Add to shopping cart", methods=['POST'])
    def shopping_cart(self, request, pk=None):
        """ Adds a recipe to the shopping cart. """
        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe in cart.recipes.all():
            return Response(
                {'errors': 'Already in the shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart.recipes.add(recipe)
        return Response(RecipeLiteSerializer(recipe).data)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        """ Removes a recipe from the shopping cart. """
        recipe = get_object_or_404(Recipe, id=pk)
        cart = get_object_or_404(ShoppingCart, user=request.user)
        if recipe not in cart.recipes.all():
            return Response(
                {'errors': 'Not in the shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, name="Add to favourites", methods=['POST'])
    def favorite(self, request, pk=None):
        """ Adds a recipe to favourites. """
        favourites, _ = Favourites.objects.get_or_create(user=request.user)
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe in favourites.recipes.all():
            return Response(
                {'errors': 'Already in favourites.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favourites.recipes.add(recipe)
        return Response(RecipeLiteSerializer(recipe).data)

    @favorite.mapping.delete
    def remove_from_favourites(self, request, pk=None):
        """ Removes a recipe from favourites. """
        recipe = get_object_or_404(Recipe, id=pk)
        favourites = get_object_or_404(Favourites, user=request.user)
        if recipe not in favourites.recipes.all():
            return Response(
                {'errors': 'Not in favourites.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favourites.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        """ Returns the shopping cart aggregated contents as a file. """
        recipes = (
            request.user.shoppingcart.recipes.prefetch_related('ingredients')
        )
        ingredients = (
            recipes.order_by('ingredients__name')
            .values('ingredients__name', 'ingredients__measurement_unit')
            .annotate(total=Sum('recipeingredients__amount'))
        )
        ingredients_list = ''
        for ingredient in ingredients:
            ingredients_list += (
                f'{ingredient.get("ingredients__name")}'
                f' — {ingredient.get("total")}'
                f' {ingredient.get("ingredients__measurement_unit")}.\r\n'
            )
        response = HttpResponse(
            ingredients_list, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={"shopping_list.txt"}'
        )
        return response
