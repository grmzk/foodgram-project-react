from rest_framework import serializers

from recipes.models import IngredientRecipe


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )
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
        model = IngredientRecipe
