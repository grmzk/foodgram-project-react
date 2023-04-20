from rest_framework import mixins, viewsets


class ListRetrieveCreateModelViewSet(mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.CreateModelMixin,
                                     viewsets.GenericViewSet):
    pass


class ListRetrieveModelViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    pass
