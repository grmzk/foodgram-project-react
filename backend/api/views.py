from django.db.models import Exists, OuterRef, Prefetch
from django.db.models.expressions import Value
from django_filters import rest_framework
from djoser import utils as djoser_utils
from djoser.conf import settings as djoser_settings
from djoser.views import TokenCreateView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscription, User

from .filters import RecipeFilter
from .paginations import PageNumberLimitPagination
from .permissions import IsAuthOrListOnlyPermission, IsAuthorOrGetOrPost
from .serializers import (IngredientSerializer, RecipeSerializer,
                          TagSerializer, UserSerializer,
                          UserSetPasswordSerializer)
from .viewsets import ListRetrieveCreateModelViewSet, ListRetrieveModelViewSet


class UserViewSet(ListRetrieveCreateModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']
    pagination_class = PageNumberLimitPagination
    permission_classes = [IsAuthOrListOnlyPermission]

    def get_queryset(self):
        current_user = self.request.user
        is_subscribed = (
            Exists(Subscription.objects.filter(author_id=OuterRef('id'),
                                               user_id=current_user.id))
        )
        return User.objects.all().annotate(is_subscribed=is_subscribed)

    @action(detail=False, methods=['GET'], url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def me_action(self, request):
        instance = self.get_queryset().get(id=self.request.user.id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='set_password',
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=UserSetPasswordSerializer)
    def set_password_action(self, request):
        current_user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user.set_password(serializer.validated_data['new_password'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenCreateResponse201View(TokenCreateView):
    def _action(self, serializer):
        token = djoser_utils.login_user(self.request, serializer.user)
        token_serializer_class = djoser_settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(ListRetrieveModelViewSet):
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageNumberLimitPagination
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrGetOrPost]

    def get_queryset(self):
        current_user = self.request.user
        author_prefetch = Prefetch('author',
                                   queryset=UserViewSet.get_queryset(self))
        is_favorited = Value(False)
        is_in_shopping_cart = Value(False)
        if not current_user.is_anonymous:
            is_favorited = (
                Exists(current_user.favorite.filter(id=OuterRef('id')))
            )
            is_in_shopping_cart = (
                Exists(current_user.shopping_cart.filter(id=OuterRef('id')))
            )
        return (Recipe.objects
                .prefetch_related(author_prefetch)
                .prefetch_related('tags')
                .prefetch_related('ingredients__ingredient'
                                  '__measurement_unit')
                .all()
                .annotate(is_favorited=is_favorited)
                .annotate(is_in_shopping_cart=is_in_shopping_cart))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
