from rest_framework import mixins, viewsets


class NonPartialUpdateModelViewSet(viewsets.ModelViewSet):
    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class ListRetrieveCreateModelViewSet(mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.CreateModelMixin,
                                     viewsets.GenericViewSet):
    pass


class ListRetrieveModelViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    pass
