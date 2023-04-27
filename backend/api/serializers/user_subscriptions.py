from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User

from ..serializers import RecipeSerializer


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)
    recipes = RecipeSerializer(fields=['id', 'name', 'image', 'cooking_time'],
                               many=True, read_only=True)

    class Meta:
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count', 'recipes']
        read_only_fields = fields
        model = User

    def __init__(self, *args, **kwargs):
        self.recipes_limit = kwargs.pop('recipes_limit', None)
        if self.recipes_limit:
            try:
                self.recipes_limit = int(self.recipes_limit)
            except ValueError:
                raise ValidationError('Query param `recipes_limit` '
                                      'must be integer!')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.recipes_limit:
            representation['recipes'] = (
                representation['recipes'][:self.recipes_limit]
            )
        return representation
