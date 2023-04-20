from djoser import utils as djoser_utils
from djoser.conf import settings as djoser_settings
from djoser.views import TokenCreateView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User

from .paginations import PageNumberLimitPagination
from .permissions import IsAuthOrListOnlyPermission
from .serializers import UserSerializer, UserSetPasswordSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']
    pagination_class = PageNumberLimitPagination
    permission_classes = [IsAuthOrListOnlyPermission]

    @action(detail=False, methods=['GET'], url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def me_action(self, request):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='set_password',
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=UserSetPasswordSerializer)
    def set_password_action(self, request):
        current_user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user.set_password(serializer.validated_data['new_password'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenCreateResponse201View(TokenCreateView):
    def _action(self, serializer):
        token = djoser_utils.login_user(self.request, serializer.user)
        token_serializer_class = djoser_settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )
