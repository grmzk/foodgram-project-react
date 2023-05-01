from rest_framework import permissions

from recipes.models import Tag

from ..mixins import ListRetrieveModelViewSet
from ..serializers import TagSerializer


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]
