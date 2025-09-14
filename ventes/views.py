from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Vente, LigneVente
from .serializers import VenteSerializer, LigneVenteSerializer
from produits.models import Produit
from produits.serializers import ProduitSerializer
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

class VenteViewSet(viewsets.ModelViewSet):
    """
    Point d'API permettant de gérer les ventes avec plusieurs produits.

    Permissions :
    - lister, récupérer : Admin, Admin Secondaire ou Artisan (pour leurs propres ventes)
    - créer : Admin ou Artisan
    - mettre à jour, mise à jour partielle, supprimer : Admin uniquement
    """
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer

    def get_permissions(self):
        """
        Définit les permissions en fonction de l'action.
        - Lecture : utilisateurs authentifiés
        - Écriture : administrateurs uniquement
        """
        if self.action in ['list', 'retrieve', 'artisan_products']:
            # Lecture seule pour tout utilisateur authentifié
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Création, mise à jour et suppression réservées aux administrateurs
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def check_permissions(self, request):
        """
        Vérifie que l'utilisateur a la permission d'effectuer l'action demandée.
        """
        super().check_permissions(request)
        
        # Si c'est une action d'écriture, vérifier que l'utilisateur est admin
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if not request.user.is_authenticated or request.user.user_type not in ['admin', 'secondary_admin']:
                raise PermissionDenied("Seuls les administrateurs peuvent effectuer cette action.")

    def get_queryset(self):
        """
        Filtre le queryset en fonction du rôle de l'utilisateur.
        - Les administrateurs voient toutes les ventes
        - Les artisans voient uniquement leurs ventes
        - Les autres utilisateurs ne voient rien
        """
        user = self.request.user
        if not user.is_authenticated:
            return Vente.objects.none()
            
        queryset = Vente.objects.all().select_related('artisan')
        
        # Pour les administrateurs, retourner toutes les ventes
        if user.user_type in ['admin', 'secondary_admin']:
            return queryset.prefetch_related('lignes_vente', 'lignes_vente__product')
            
        # Pour les artisans, retourner uniquement leurs ventes
        if user.user_type == 'artisan':
            return queryset.filter(artisan=user.artisan_profile).prefetch_related(
                'lignes_vente', 
                'lignes_vente__product',
                'lignes_vente__product__categorie'
            )
            
        # Par défaut, ne rien retourner
        return Vente.objects.none()

    def get_serializer_context(self):
        """Ajoute la requête au contexte du sérialiseur."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_serializer_context(self):
        """Ajoute la requête au contexte du sérialiseur."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
        
    @action(detail=False, methods=['get'], url_path='artisan-products/(?P<artisan_id>[^/.]+)')
    def artisan_products(self, request, artisan_id=None):
        """
        Endpoint pour récupérer les produits d'un artisan spécifique.
        Utile pour le formulaire de vente où on sélectionne d'abord un artisan,
        puis on affiche uniquement ses produits.
        """
        user = request.user
        
        # Vérifier que l'utilisateur a le droit d'accéder aux produits de cet artisan
        if user.user_type == 'artisan' and str(user.artisan_profile.id) != artisan_id:
            return Response(
                {"detail": "Vous n'avez pas la permission d'accéder à ces produits."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Récupérer les produits de l'artisan avec stock > 0
            products = Produit.objects.filter(
                artisan_id=artisan_id,
                stock__gt=0  # Ne récupérer que les produits en stock
            ).select_related('categorie').order_by('name')
            
            serializer = ProduitSerializer(
                products, 
                many=True,
                context={'request': request}  # Pour les URLs absolues des images
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des produits de l'artisan {artisan_id}: {str(e)}")
            return Response(
                {"detail": "Une erreur est survenue lors de la récupération des produits."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        Crée une nouvelle vente avec des produits identifiés par leur nom.
        Format attendu :
        {
            "artisan_name": "Nom de l'artisan",  # Optionnel pour les artisans
            "lignes_vente": [
                {
                    "product_name": "Nom du produit",
                    "quantity": 2,
                    "artisan_name": "Nom de l'artisan"  # Optionnel
                }
            ]
        }
        """
        try:
            # Faire une copie mutable des données de la requête
            data = request.data.copy()
            
            # Vérifier que les lignes de vente sont fournies
            if 'lignes_vente' not in data or not data['lignes_vente']:
                return Response(
                    {"lignes_vente": ["Au moins un produit est requis pour la vente."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Pour les artisans, définir automatiquement l'artisan
            if request.user.user_type == 'artisan':
                data['artisan_name'] = request.user.get_full_name() or request.user.artisan_profile.raison_sociale
            # Pour les administrateurs, vérifier que l'artisan est spécifié
            elif 'artisan_name' not in data:
                return Response(
                    {"artisan_name": ["Le nom de l'artisan est requis pour les utilisateurs non-artisans."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Valider et créer la vente
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            # Utiliser une transaction pour assurer l'intégrité des données
            with transaction.atomic():
                # Créer la vente
                vente = serializer.save()
                
                # Récupérer la vente avec toutes les relations nécessaires
                vente = Vente.objects.prefetch_related(
                    'lignes_vente', 
                    'lignes_vente__product',
                    'artisan',
                    'artisan__user'
                ).get(pk=vente.id)
                
                # Journaliser la création de la vente
                logger.info(f"Nouvelle vente créée : {vente.numero_vente} avec {vente.lignes_vente.count()} produits")
                
                # Retourner la réponse avec les données complètes
                response_serializer = self.get_serializer(vente)
                headers = self.get_success_headers(response_serializer.data)
                
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
                
        except ValidationError as e:
            logger.warning(f"Erreur de validation lors de la création de la vente: {str(e)}")
            return Response(
                e.detail if hasattr(e, 'detail') else {"detail": "Données invalides", "errors": e.dict()},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la création de la vente: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Une erreur est survenue lors de la création de la vente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
