from django.db.models import Exists, OuterRef, Prefetch
from django.db.models.expressions import Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe
from users.models import User

from ..filters import RecipeFilter
from ..paginations import PageNumberLimitPagination
from ..permissions import IsAuthorOrGetOrPost
from ..serializers import RecipeSerializer
from ..utils import is_subscribed


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
        author_prefetch = Prefetch(
            'author',
            queryset=User.objects.all().annotate(
                is_subscribed=is_subscribed(current_user.id)
            )
        )
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

    @staticmethod
    def gen_shopping_cart_content(recipes):
        header = ('---------СПИСОК ПОКУПОК---------\n'
                  '================================\n')
        footer = ('================================\n'
                  '----------FOODGRAM (\u2184)----------')
        data = dict()
        for recipe in recipes:
            for ingredient_amount in recipe.ingredients.all():
                ingredient = ingredient_amount.ingredient
                data[ingredient] = (
                    data.get(ingredient, 0) + ingredient_amount.amount
                )
        body = str()
        for ingredient, amount in data.items():
            body += (f'{ingredient.name} - {amount} '
                     f'{ingredient.measurement_unit.name}\n')
        return header + body + footer

    @action(detail=False, methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart_action(self, request):
        recipes = (request.user.shopping_cart
                   .prefetch_related('ingredients__ingredient'
                                     '__measurement_unit').all())
        content = self.gen_shopping_cart_content(recipes)
        filename = f'{request.user.username}_shopping_cart.txt'
        headers = {
            'Content-Type': 'text/plain',
            'Content-Disposition': f'attachment; filename="{filename}"',
        }
        return HttpResponse(content, headers=headers,
                            status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart_action(self, request, pk):
        recipe = get_object_or_404(self.get_queryset(), id=pk)
        if recipe in request.user.shopping_cart.all():
            data = {'errors': 'Recipe is already in the shopping cart!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        request.user.shopping_cart.add(recipe)
        fields = ['id', 'name', 'image', 'cooking_time']
        serializer = self.get_serializer(recipe, fields=fields)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart_action.mapping.delete
    def shopping_cart_delete_action(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe not in request.user.shopping_cart.all():
            data = {'errors': 'Recipe is not in the shopping cart!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        request.user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def favorite_action(self, request, pk):
        recipe = get_object_or_404(self.get_queryset(), id=pk)
        if recipe in request.user.favorite.all():
            data = {'errors': 'Recipe is already in the favorite!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        request.user.favorite.add(recipe)
        fields = ['id', 'name', 'image', 'cooking_time']
        serializer = self.get_serializer(recipe, fields=fields)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @favorite_action.mapping.delete
    def favorite_delete_action(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe not in request.user.favorite.all():
            data = {'errors': 'Recipe is not in favorite!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        request.user.favorite.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
