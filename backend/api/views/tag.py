from rest_framework import permissions

from recipes.models import Tag

from ..serializers import TagSerializer
from ..viewsets import ListRetrieveModelViewSet


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]
