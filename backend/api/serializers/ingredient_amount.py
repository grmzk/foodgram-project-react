from rest_framework import serializers

from recipes.models import IngredientAmount


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
