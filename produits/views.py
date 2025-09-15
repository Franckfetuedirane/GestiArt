# produits/views.py
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer
from artisans.models import Artisan
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        nom = request.data.get('nom', '').lower().strip()
        if nom and Categorie.objects.filter(nom__iexact=nom).exists():
            return Response(
                {"error": "Une catégorie avec ce nom existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

class ProduitViewSet(viewsets.ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['categorie', 'artisan']

    def get_queryset(self):
        queryset = Produit.objects.all()
        categorie = self.request.query_params.get('categorie')
        artisan = self.request.query_params.get('artisan')
        
        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
        if artisan:
            queryset = queryset.filter(artisan_id=artisan)
            
        return queryset

    def create(self, request, *args, **kwargs):
        logger.info(f"Données reçues : {request.data}")
        
        if not request.user.is_staff:
            return Response(
                {"error": "Seuls les administrateurs peuvent ajouter des produits"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        
        # Vérifier si un artisan est spécifié
        artisan_id = data.get('artisan')
        if not artisan_id:
            return Response(
                {"error": "Veuillez sélectionner un artisan."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Vérifier que l'artisan existe
        try:
            artisan = Artisan.objects.get(pk=artisan_id)
        except (ValueError, Artisan.DoesNotExist):
            return Response(
                {"error": "L'artisan sélectionné n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.error(f"Erreur de validation : {serializer.errors}")
            return Response(
                {"error": "Données invalides", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            logger.error(f"Erreur lors de la création du produit : {str(e)}")
            return Response(
                {"error": f"Erreur serveur : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]