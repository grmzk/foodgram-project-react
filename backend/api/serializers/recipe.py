from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import empty
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
    image = Base64ImageField()
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

    def run_validation(self, data=empty):
        try:
            return super().run_validation(data)
        except Exception as error:
            ingredients = data.get('ingredients', None)
            if ingredients:
                # Deleting orphans which created
                # in IngredientsRelatedField's to_internal_value() method.
                for ingredient in ingredients:
                    IngredientRecipe.objects.filter(
                        ingredient_id=ingredient['id'],
                        amount=ingredient['amount'],
                        recipe=None,
                    ).delete()
            raise error

    @staticmethod
    def validate_ingredients(ingredients):
        ingredient_ids = list()
        for ingredient_recipe in ingredients:
            ingredient_id = ingredient_recipe.ingredient.id
            if ingredient_id in ingredient_ids:
                raise ValidationError('Two identical ingredients found!')
            ingredient_ids.append(ingredient_id)
        return ingredients
