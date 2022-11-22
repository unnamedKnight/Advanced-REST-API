from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view

from .serializers import UserSerializer

# Create your views here.


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


# class CreateTokenView(ObtainAuthToken):
#     serializer_class = AuthTokenSerializer
#     # adding render_classes manually because
#     # Token create view doesn't support browsable Api By Default
#     # so we add it manually to get the browsable Api
#     # In the token create view
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


@api_view(
    [
        "POST",
    ]
)
def logout_user(request):
    if request.method == "POST":
        request.user.auth_token.delete()
        # logout(request)
        return Response(status=status.HTTP_200_OK)
