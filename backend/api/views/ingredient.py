from rest_framework import permissions

from recipes.models import Ingredient

from ..serializers import IngredientSerializer
from ..mixins import ListRetrieveModelViewSet


class IngredientViewSet(ListRetrieveModelViewSet):
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return self.queryset
