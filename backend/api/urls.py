from recipes.views import IngredientsViewSet, RecipesViewSet, TagsViewSet
from rest_framework.routers import DefaultRouter

from django.urls import include, path

from users.views import FollowViewSet


router = DefaultRouter()
router.register(r'users', FollowViewSet, basename='following')
router.register(r'tags', TagsViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipesViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
