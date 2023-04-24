from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from recipes.validators import min_cooking_time_validator
from users.models import User
from users.validators import username_regex_validator

from .serializer_fields import (Base64ImageField, IngredientsRelatedField,
                                TagsPrimaryKeyRelatedField)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150,
                                     validators=[username_regex_validator])
    is_subscribed = serializers.BooleanField(read_only=True)
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'password', 'is_subscribed']
        model = User

    def get_fields(self):
        fields = super().get_fields()
        method = self.context['request'].method
        if method == 'POST':
            del fields['is_subscribed']
        return fields

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150, required=True,
                                         write_only=True)
    current_password = serializers.CharField(max_length=150, required=True,
                                             write_only=True)

    class Meta:
        fields = ['new_password', 'current_password']

    def validate_current_password(self, current_password):
        current_user = self.context['request'].user
        if not current_user.check_password(current_password):
            raise ValidationError('Неверный пароль!')
        return current_password


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'slug', 'color']
        read_only_fields = fields
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(
        source='measurement_unit.name'
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = fields
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit.name',
        read_only=True
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = fields
        model = IngredientAmount


class RecipeSerializer(serializers.ModelSerializer):
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
