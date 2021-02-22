from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserAPIView(generics.CreateAPIView):
    """
        Register new user
    """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """
        Create new token for the user
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
