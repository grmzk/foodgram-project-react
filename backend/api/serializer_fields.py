import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import Ingredient


class IngredientsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        from api.serializers import IngredientAmountSerializer
        return IngredientAmountSerializer(context=self.context,
                                          instance=value).data

    def to_internal_value(self, data):
        ingredient = get_object_or_404(Ingredient, id=data['id'])
        return self.queryset.create(ingredient=ingredient,
                                    amount=data['amount'])


class TagsPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        from api.serializers import TagSerializer
        return TagSerializer(context=self.context, instance=value).data

    def to_internal_value(self, data):
        get_object_or_404(self.queryset, id=data)
        return super().to_internal_value(data)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if not (isinstance(data, str) and data.startswith('data:image')):
            raise ValidationError('Image must be in base64 format!')
        image_format, image_str = data.split(';base64,')
        ext = image_format.split('/')[-1]
        data = ContentFile(base64.b64decode(image_str), name='image.' + ext)
        return super().to_internal_value(data)
