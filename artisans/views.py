from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Artisan
from .serializers import ArtisanSerializer
from users.permissions import IsAdminUser, IsSecondaryAdminUser, IsAdminOrArtisanOwner
from users.models import User
from rest_framework import serializers

# Create your views here.

class ArtisanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows artisans to be viewed, created, updated or deleted.

    Permissions:
    - list: Admin, Secondary Admin
    - retrieve: Admin, Secondary Admin, or Artisan owner
    - create, update, partial_update, destroy: Admin only
    """
    queryset = Artisan.objects.all()
    serializer_class = ArtisanSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAdminUser | IsSecondaryAdminUser]
        elif self.action == 'retrieve':
            permission_classes = [IsAdminUser | IsSecondaryAdminUser | IsAdminOrArtisanOwner]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Save the new artisan instance.
        If the user is an admin, `user_id` must be provided in the request data.
        The associated user's `user_type` will be set to 'artisan'.
        """
        user_id = self.request.data.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            if user.user_type != 'artisan':
                user.user_type = 'artisan'
                user.save()
            serializer.save(user=user)
        else:
            # If no user_id is provided, it implies the current authenticated user (admin) is creating an artisan profile for themselves
            # This scenario is less common for an admin creating their *own* artisan profile, but could be for simplicity
            # For strictness, could raise a validation error here if user_id is missing for admin
            raise serializers.ValidationError({'user_id': 'This field is required for admin users creating an artisan profile.'})
