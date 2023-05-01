from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import IngredientAmount, Recipe, Tag
from recipes.validators import min_cooking_time_validator

from ..serializer_fields import (IngredientsRelatedField,
                                 TagsPrimaryKeyRelatedField)
from ..serializers import DynamicFieldsModelSerializer
from ..serializers.user import UserSerializer


class RecipeSerializer(DynamicFieldsModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredients = IngredientsRelatedField(
        queryset=IngredientAmount.objects.all(),
        many=True,
    )
    cooking_time = serializers.IntegerField(
        validators=[min_cooking_time_validator]
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        fields = ['id', 'author', 'tags', 'name', 'text',
                  'image', 'ingredients', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']
        model = Recipe
