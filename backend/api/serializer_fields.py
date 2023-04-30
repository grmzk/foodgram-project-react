import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import Ingredient
from recipes.validators import min_amount_validator

from .serializers import IngredientAmountSerializer
from .serializers.tag import TagSerializer
from .validators import integer_validator


class IngredientsRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return IngredientAmountSerializer(context=self.context,
                                          instance=value).data

    def to_internal_value(self, data):
        value_name = 'amount'
        data[value_name] = integer_validator(value_name, data['amount'])
        min_amount_validator(data['amount'])
        if not Ingredient.objects.filter(id=data['id']).exists():
            raise ValidationError(f'Ingredient with `id=={data["id"]}` '
                                  'not exists!')
        ingredient_amount, _ = self.queryset.get_or_create(
            ingredient_id=data['id'],
            amount=data['amount']
        )
        return ingredient_amount


class TagsPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return TagSerializer(context=self.context, instance=value).data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if not (isinstance(data, str) and data.startswith('data:image')):
            raise ValidationError('Image must be in base64 format!')
        image_format, image_str = data.split(';base64,')
        ext = image_format.split('/')[-1]
        data = ContentFile(base64.b64decode(image_str), name='image.' + ext)
        return super().to_internal_value(data)
