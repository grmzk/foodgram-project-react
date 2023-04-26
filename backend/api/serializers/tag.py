from rest_framework import serializers

from recipes.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'slug', 'color']
        read_only_fields = fields
        model = Tag
