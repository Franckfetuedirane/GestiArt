from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Vente
from .serializers import VenteSerializer
from users.permissions import IsAdminUser, IsArtisanUser, IsSecondaryAdminUser, IsAdminOrArtisanOwner

# Create your views here.

class VenteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sales to be viewed, created, updated or deleted.

    Permissions:
    - list, retrieve: Admin, Secondary Admin, or Artisan (for their own sales)
    - create: Admin or Artisan
    - update, partial_update, destroy: Admin only
    """
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAdminUser | IsSecondaryAdminUser | IsArtisanUser]
        elif self.action in ['create']:
            permission_classes = [IsAdminUser | IsArtisanUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filters the queryset based on the user's role.
        Artisans can only see sales related to their products.
        Admins and secondary admins can see all sales.
        """
        user = self.request.user
        if user.user_type == 'artisan':
            return Vente.objects.filter(artisan__user=user)
        return super().get_queryset()
