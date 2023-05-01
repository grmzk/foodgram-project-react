from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Subscription, User

from ..mixins import ListRetrieveCreateModelViewSet
from ..paginations import PageNumberLimitPagination
from ..permissions import IsAuthOrListOnlyPermission
from ..serializers import (UserSerializer, UserSetPasswordSerializer,
                           UserSubscriptionsSerializer)
from ..utils import is_subscribed


class UserViewSet(ListRetrieveCreateModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageNumberLimitPagination
    permission_classes = [IsAuthOrListOnlyPermission]

    def get_queryset(self):
        return User.objects.annotate(
            is_subscribed=is_subscribed(self.request.user.id)
        )

    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def me_action(self, request):
        instance = self.get_queryset().get(id=request.user.id)
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

    def get_user_subscriptions_queryset(self):
        return (User.objects
                .prefetch_related('recipes')
                .annotate(is_subscribed=is_subscribed(self.request.user.id))
                .annotate(recipes_count=Count('recipes'))
                .order_by('username'))

    @action(detail=False, methods=['get'],
            url_path='subscriptions',
            serializer_class=UserSubscriptionsSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions_action(self, request):
        authors = (self.get_user_subscriptions_queryset()
                   .filter(following__user_id=self.request.user.id))
        paginated_authors = self.paginate_queryset(authors)
        recipes_limit = request.query_params.get('recipes_limit', None)
        serializer = self.get_serializer(paginated_authors,
                                         recipes_limit=recipes_limit,
                                         many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'],
            url_path='subscribe',
            serializer_class=UserSubscriptionsSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe_action(self, request, pk):
        author = get_object_or_404(self.get_user_subscriptions_queryset(),
                                   id=pk)
        if author.is_subscribed:
            data = {'errors': 'Subscription on this author already exists!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(user=request.user, author=author)
        recipes_limit = request.query_params.get('recipes_limit', None)
        data = self.get_serializer(author, recipes_limit=recipes_limit).data
        data['is_subscribed'] = True
        return Response(data=data, status=status.HTTP_201_CREATED)

    @subscribe_action.mapping.delete
    def shopping_cart_delete_action(self, request, pk):
        author = get_object_or_404(User, id=pk)
        subscription = Subscription.objects.filter(user_id=request.user.id,
                                                   author_id=author.id)
        if not subscription.exists():
            data = {'errors': 'Subscription on this author not exists!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
