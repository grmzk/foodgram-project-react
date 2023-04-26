from django.db.models import Exists, OuterRef
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Subscription, User

from ..paginations import PageNumberLimitPagination
from ..permissions import IsAuthOrListOnlyPermission
from ..serializers import UserSerializer, UserSetPasswordSerializer
from ..viewsets import ListRetrieveCreateModelViewSet


class UserViewSet(ListRetrieveCreateModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']
    pagination_class = PageNumberLimitPagination
    permission_classes = [IsAuthOrListOnlyPermission]

    def get_queryset(self):
        current_user = self.request.user
        is_subscribed = (
            Exists(Subscription.objects.filter(author_id=OuterRef('id'),
                                               user_id=current_user.id))
        )
        return User.objects.all().annotate(is_subscribed=is_subscribed)

    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def me_action(self, request):
        instance = self.get_queryset().get(id=self.request.user.id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='set_password',
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=UserSetPasswordSerializer)
    def set_password_action(self, request):
        current_user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user.set_password(serializer.validated_data['new_password'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(detail=False, methods=['get'],
    #         url_path='subscriptions',
    #         permission_classes=[permissions.IsAuthenticated])
    # def subscriptions_action(self, request):
    #     subscriptions = request.user.follower.all().annotate(test=Value(True))
    #     authors = [item.author for item in subscriptions]
    #     paginated = self.paginate_queryset(authors)
    #     serializer = self.get_serializer(paginated, many=True)
    #     print(type(serializer.data))
    #     return self.get_paginated_response(serializer.data)

    # @action(detail=True, methods=['post'],
    #         url_path='shopping_cart',
    #         permission_classes=[permissions.IsAuthenticated])
    # def shopping_cart_action(self, request, pk):
    #     recipe = get_object_or_404(self.get_queryset(), id=pk)
    #     if recipe in request.user.shopping_cart.all():
    #         data = {'errors': 'Recipe is already in the shopping cart!'}
    #         return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    #     request.user.shopping_cart.add(recipe)
    #     serializer = self.get_serializer(recipe)
    #     keys = ['id', 'name', 'image', 'cooking_time']
    #     data = {key: serializer.data[key] for key in keys}
    #     return Response(data=data, status=status.HTTP_201_CREATED)
    #
    # @shopping_cart_action.mapping.delete
    # def shopping_cart_delete_action(self, request, pk):
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     if recipe not in request.user.shopping_cart.all():
    #         data = {'errors': 'Recipe is not in the shopping cart!'}
    #         return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    #     request.user.shopping_cart.remove(recipe)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
