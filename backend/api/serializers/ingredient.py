from rest_framework import serializers

from recipes.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(
        source='measurement_unit.name'
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = fields
        model = Ingredient
