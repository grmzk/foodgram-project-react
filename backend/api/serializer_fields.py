from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import Ingredient
from recipes.validators import min_amount_validator

from .serializers.ingredient_recipe import IngredientRecipeSerializer
from .serializers.tag import TagSerializer
from .validators import integer_validator


class IngredientsRelatedField(serializers.RelatedField):
    def to_representation(self, ingredient_recipe):
        return IngredientRecipeSerializer(instance=ingredient_recipe).data

    def to_internal_value(self, data):
        value_names = ['id', 'amount']
        for value_name in value_names:
            if value_name not in data.keys():
                raise ValidationError(f'Required value `{value_name}` '
                                      'not exists in ingredients field!')
            data[value_name] = integer_validator(value_name, data[value_name])
        min_amount_validator(data['amount'])
        if not Ingredient.objects.filter(id=data['id']).exists():
            raise ValidationError(f'Ingredient with `id=={data["id"]}` '
                                  'not exists!')
        # Creating orphans objects that will be adopted
        # when serializer's create or update methods done.
        return (self.queryset.create(ingredient_id=data['id'],
                                     amount=data['amount']))


class TagsPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return TagSerializer(context=self.context, instance=value).data
