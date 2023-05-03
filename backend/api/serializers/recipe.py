from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import IngredientRecipe, Recipe, Tag
from recipes.validators import min_cooking_time_validator

from ..serializer_fields import (IngredientsRelatedField,
                                 TagsPrimaryKeyRelatedField)
from ..serializers import DynamicFieldsModelSerializer
from ..serializers.user import UserSerializer


class RecipeSerializer(DynamicFieldsModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=False)
    ingredients = IngredientsRelatedField(
        source='ingredient_recipe',
        queryset=IngredientRecipe.objects.all(),
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

    def update(self, instance, validated_data):
        # Deleting current recipe's IngredientRecipe objects.
        # They will be replaced by orphans from
        # IngredientsRelatedField's to_internal_value() method.
        instance.ingredient_recipe.all().delete()
        return super().update(instance, validated_data)

    @staticmethod
    def validate_ingredients(ingredients):
        ingredient_ids = list()
        for ingredient_recipe in ingredients:
            ingredient_id = ingredient_recipe.ingredient.id
            if ingredient_id in ingredient_ids:
                # Deleting orphans which created
                # in IngredientsRelatedField's to_internal_value() method.
                for item in ingredients:
                    item.delete()
                raise ValidationError('Two identical ingredients found!')
            ingredient_ids.append(ingredient_id)
        return ingredients
