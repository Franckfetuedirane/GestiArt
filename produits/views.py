from django.shortcuts import render
from rest_framework import viewsets
from .models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer
from users.permissions import IsAdminUser, IsArtisanUser, IsAdminOrReadOnly

# Create your views here.

class ProduitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed, created, updated or deleted.

    Permissions:
    - All authenticated users can list products.
    - Admins can perform all CRUD operations.
    - Artisans can only create and view their own products.
    """
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Filters the queryset based on the user's role.
        Artisans can only see their own products.
        Admins and secondary admins can see all products.
        """
        if self.request.user.user_type == 'artisan':
            return Produit.objects.filter(artisan__user=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):
        """
        Associates the current user as the artisan when creating a new product.
        Only admins can specify a different artisan.
        """
        if self.request.user.user_type == 'artisan':
            # For artisans, automatically associate them as the product's artisan
            artisan = Artisan.objects.get(user=self.request.user)
            serializer.save(artisan=artisan)
        else:
            # For admins, use the provided artisan or default to the current user's artisan profile if exists
            if 'artisan' not in serializer.validated_data:
                try:
                    artisan = Artisan.objects.get(user=self.request.user)
                    serializer.save(artisan=artisan)
                except Artisan.DoesNotExist:
                    serializer.save()


class CategorieViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour gérer les catégories.
    
    Permissions :
    - Tous les utilisateurs authentifiés peuvent lister les catégories.
    - Seuls les administrateurs peuvent créer, modifier ou supprimer des catégories.
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """
        Retourne toutes les catégories triées par nom.
        """
        return Categorie.objects.all().order_by('nom')
