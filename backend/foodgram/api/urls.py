from django.urls import include, path
from users.views import Subscribe
from rest_framework.routers import DefaultRouter
from recipes.views import TagsViewSet, IngredientsViewSet, RecipesViewSet

router = DefaultRouter()
# router.register(r'users', Subscribe.as_view(), basename='following')
router.register(r'tags', TagsViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipesViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
