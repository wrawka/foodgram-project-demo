from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import AllowAny
from .models import Tag, Ingredient, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True, name="Add to shopping cart", methods=['POST'])
    def shopping_cart(self, request, pk=None):
        """ Add recipe to the shopping cart. """
        
        pass
        

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        """ Remove recipe from the shopping cart. """
        pass
