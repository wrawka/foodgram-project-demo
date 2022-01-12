from django.urls import include, path
from users.views import FollowViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', FollowViewSet, basename='following')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]