from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, TagViewSet, TokenCreateResponse201View,
                    UserViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')


auth_patterns = [
    path('token/login/', TokenCreateResponse201View.as_view()),
    path('token/logout/', TokenDestroyView.as_view()),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_patterns))
]
