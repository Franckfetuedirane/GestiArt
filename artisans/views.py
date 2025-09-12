from rest_framework import viewsets, permissions
from .models import Artisan
from .serializers import ArtisanSerializer
from users.permissions import IsAdminUser, IsSecondaryAdminUser, IsAdminOrArtisanOwner
from rest_framework.exceptions import ValidationError

class ArtisanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows artisans to be viewed, created, updated or deleted.
    """
    queryset = Artisan.objects.all()
    serializer_class = ArtisanSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - Admin can do anything.
        - Secondary Admin can list and retrieve.
        - Artisan can retrieve their own profile.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action == 'list':
            self.permission_classes = [IsAdminUser | IsSecondaryAdminUser]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAdminOrArtisanOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        When an admin creates an artisan profile, the `user_id` must be provided.
        The associated user's `user_type` is expected to be 'artisan'.
        """
        user = serializer.validated_data.get('user')
        if not user:
            raise ValidationError({'user_id': 'This field is required.'})

        # Optionally, enforce that the user must be of type 'artisan'
        if user.user_type != 'artisan':
            # Or automatically update it:
            # user.user_type = 'artisan'
            # user.save()
            pass # For now, we assume the user is already an artisan

        serializer.save()
