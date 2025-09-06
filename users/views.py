from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, RegisterSerializer
from .models import User
from .permissions import IsAdminUser, IsArtisanUser, IsSecondaryAdminUser

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows any user to register with an email, password, and user_type.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserListView(generics.ListAPIView):
    """
    API endpoint for listing all users.
    Accessible only by Admin or Secondary Admin users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsSecondaryAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a specific user.
    Accessible only by Admin users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
