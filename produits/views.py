from django.shortcuts import render
from rest_framework import viewsets
from .models import Produit
from .serializers import ProduitSerializer
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
        Performs creation of a product.
        If the user is an admin, `artisan_id` must be provided in the request data.
        If the user is an artisan, the product is automatically associated with their profile.
        """
        if self.request.user.user_type == 'admin':
            artisan_id = self.request.data.get('artisan_id')
            if not artisan_id:
                raise serializers.ValidationError({'artisan_id': 'This field is required for admin users.'})
            serializer.save(artisan_id=artisan_id)
        else:
            # For artisan users, associate the product with their own artisan profile
            serializer.save(artisan=self.request.user.artisan_profile)
