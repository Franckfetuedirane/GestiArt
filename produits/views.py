from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer
from users.permissions import IsAdminUser, IsArtisanUser, IsAdminOrArtisanOwner
from artisans.models import Artisan
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class ProduitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed, created, updated or deleted.

    Permissions:
    - All authenticated users can list products.
    - Admins can perform all CRUD operations.
    - Artisans can only create, view, update and delete their own products.
    """
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrArtisanOwner]

    def get_queryset(self):
        """
        Filters the queryset based on the user's role.
        Artisans can only see their own products.
        Admins can see all products.
        """
        queryset = super().get_queryset()
        if self.request.user.user_type == 'artisan':
            return queryset.filter(artisan__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        """
        Associates the current user as the artisan when creating a new product.
        Only admins can specify a different artisan.
        """
        if self.request.user.user_type == 'artisan':
            # For artisans, automatically associate them as the product's artisan
            artisan = get_object_or_404(Artisan, user=self.request.user)
            serializer.save(artisan=artisan)
        else:
            # For admins, use the provided artisan or default to the current user's artisan profile if exists
            if 'artisan' not in serializer.validated_data:
                try:
                    artisan = Artisan.objects.get(user=self.request.user)
                    serializer.save(artisan=artisan)
                except Artisan.DoesNotExist:
                    serializer.save()
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAdminUser | IsArtisanUser]
        else:
            permission_classes = [IsAdminOrArtisanOwner]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle soft delete for products.
        """
        instance = self.get_object()
        if request.user.user_type == 'artisan':
            # For artisans, do soft delete (set is_active to False)
            instance.is_active = False
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # For admins, do hard delete
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategorieViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour gérer les catégories.
    
    Permissions :
    - Tous les utilisateurs authentifiés peuvent lister les catégories.
    - Seuls les administrateurs peuvent créer, modifier ou supprimer des catégories.
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.IsAdminUser | permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Retourne toutes les catégories triées par nom.
        """
        return Categorie.objects.all().order_by('nom')
