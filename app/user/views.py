from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserAPIView(generics.CreateAPIView):
    """
        Register new user
    """
    serializer_class = UserSerializer
