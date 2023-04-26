from djoser import utils as djoser_utils
from djoser.conf import settings as djoser_settings
from djoser.views import TokenCreateView
from rest_framework import status
from rest_framework.response import Response


class TokenCreateResponse201View(TokenCreateView):
    def _action(self, serializer):
        token = djoser_utils.login_user(self.request, serializer.user)
        token_serializer_class = djoser_settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )
