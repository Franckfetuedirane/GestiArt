from rest_framework import viewsets, serializers
from .models import Produit
from .serializers import ProduitSerializer
from users.permissions import IsAdminUser, IsArtisanUser, IsAdminOrReadOnly

class ProduitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed, created, updated or deleted.

    Permissions:
    - Admins can perform all CRUD operations.
    - Artisans can only create and view their own products.
    - Other authenticated users can only view products.
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
        user = self.request.user
        if user.is_authenticated and user.user_type == 'artisan':
            return Produit.objects.filter(artisan__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        """
        Performs creation of a product.
        If the user is an artisan, the product is automatically associated with their profile.
        If the user is an admin, `artisan_id` must be provided.
        """
        user = self.request.user
        if user.user_type == 'artisan':
            serializer.save(artisan=user.artisan_profile)
        elif user.user_type == 'admin':
            artisan_id = self.request.data.get('artisan_id')
            if not artisan_id:
                raise serializers.ValidationError({'artisan_id': 'This field is required for admin users.'})
            serializer.save()
        else:
            # This case should ideally be blocked by permissions, but as a safeguard:
            serializer.save()
