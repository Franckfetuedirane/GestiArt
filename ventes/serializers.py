import json
import logging
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import Vente, LigneVente
from produits.models import Produit
from produits.serializers import ProduitSerializer
from artisans.models import Artisan
from artisans.serializers import ArtisanSerializer

logger = logging.getLogger(__name__)

class LigneVenteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les lignes de vente.
    Permet de gérer les produits d'une vente par leur ID.
    """
    product_id = serializers.UUIDField(write_only=True, required=True)
    product_details = ProduitSerializer(source='product', read_only=True)
    sous_total = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
        source='get_sous_total'
    )
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = LigneVente
        fields = [
            'id', 'product', 'product_id', 'product_name', 'product_details', 
            'quantity', 'unit_price', 'sous_total'
        ]
        read_only_fields = ['product', 'unit_price', 'sous_total', 'product_name']

    def validate(self, data):
        """Valide que le produit existe et appartient à l'artisan"""
        artisan = self.context.get('artisan')
        product_id = data.get('product_id')
        
        if not product_id:
            raise ValidationError({"product_id": "L'ID du produit est requis."})
            
        try:
            # Récupérer le produit par ID
            product = Produit.objects.get(
                id=product_id,
                artisan=artisan
            )
            
            # Vérifier la quantité
            quantity = data.get('quantity', 0)
            if quantity <= 0:
                raise ValidationError({
                    "quantity": "La quantité doit être supérieure à zéro."
                })
                
            # Vérifier le stock
            if product.stock < quantity:
                raise ValidationError({
                    "quantity": f"Stock insuffisant. Quantité disponible : {product.stock}"
                })
                
            # Ajouter le produit et son prix aux données validées
            data['product'] = product
            data['unit_price'] = product.price
            
            return data
            
        except Produit.DoesNotExist:
            raise ValidationError({
                "product_id": "Produit non trouvé ou n'appartenant pas à l'artisan."
            })
        
    def to_internal_value(self, data):
        """Convertit les noms en instances"""
        data = data.copy()
        validated_data = super().to_internal_value(data)
        
        # Ajouter le produit validé aux données
        if 'product' in validated_data:
            data['product'] = validated_data['product'].id
            
        return data

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError("La quantité doit être supérieure à zéro.")
        return value


class VenteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les ventes.
    Permet de créer des ventes avec des produits existants.
    """
    lignes_vente = LigneVenteSerializer(many=True, required=False, write_only=True)
    artisan_details = ArtisanSerializer(source='artisan', read_only=True)
    numero_vente = serializers.CharField(read_only=True)
    
    # Champ pour la sélection de l'artisan (affiché comme une liste déroulante dans l'admin)
    artisan = serializers.PrimaryKeyRelatedField(
        queryset=Artisan.objects.all(),
        required=False,
        help_text="Sélectionnez un artisan"
    )
    
    nom_du_client = serializers.CharField(
        required=True,
        help_text="Nom du client pour la vente"
    )
    
    total_amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    
    products_count = serializers.IntegerField(read_only=True)
    
    # Champ pour la sélection des produits (affiché comme des cases à cocher)
    produits = serializers.SerializerMethodField(
        read_only=True,
        help_text="Liste des produits disponibles pour la sélection"
    )
    
    # Champ pour la sélection des produits (écriture)
    produits_selectionnes = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des produits sélectionnés"
    )
    
    # Champs pour la quantité de chaque produit
    quantites = serializers.DictField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=False,
        help_text="Dictionnaire des quantités par ID de produit"
    )

    def get_artisan_products(self, obj):
        """Retourne la liste des produits de l'artisan"""
        artisan = obj.artisan if hasattr(obj, 'artisan') else None
        if not artisan:
            return []
        
        return [
            {
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'stock': p.stock
            }
            for p in artisan.produit_set.all()
        ]
    
    artisan_products = serializers.SerializerMethodField(
        read_only=True,
        help_text="Liste des produits disponibles pour l'artisan sélectionné"
    )
    
    def validate_artisan_name(self, value):
        """Valide et récupère l'artisan par son nom"""
        request = self.context.get('request')
        
        # Pour les artisans, on utilise automatiquement leur profil
        if request and request.user.user_type == 'artisan':
            return request.user.artisan_profile
            
        # Pour les autres utilisateurs, on vérifie que le nom est fourni
        if not value:
            raise serializers.ValidationError("Le nom de l'artisan est requis.")
            
        # Recherche de l'artisan par nom/prénom/raison sociale
        try:
            return Artisan.objects.get(
                Q(user__first_name__icontains=value) |
                Q(user__last_name__icontains=value) |
                Q(raison_sociale__icontains=value)
            )
        except Artisan.DoesNotExist:
            raise serializers.ValidationError(f"Aucun artisan trouvé avec le nom '{value}'")
        except Artisan.MultipleObjectsReturned:
            raise serializers.ValidationError("Plusieurs artisans correspondent à ce nom. Soyez plus précis.")
    
    def to_internal_value(self, data):
        """Convertit les noms en instances avant la validation"""
        data = data.copy()
        
        # Gérer l'artisan par nom
        if 'artisan_name' in data and data['artisan_name']:
            try:
                artisan = self.validate_artisan_name(data.pop('artisan_name'))
                data['artisan'] = artisan.id
            except serializers.ValidationError as e:
                raise serializers.ValidationError({'artisan_name': e.detail})
        
        # Supprimer les champs non reconnus
        data.pop('artisan_name', None)
        
        return super().to_internal_value(data)
    
    class Meta:
        model = Vente
        fields = [
            'id', 'numero_vente', 'artisan', 'artisan_details',
            'nom_du_client', 'sale_date', 'total_amount', 'products_count', 
            'lignes_vente', 'produits', 'produits_selectionnes', 'quantites',
            'artisan_products'  # Ajout du champ manquant
        ]
        read_only_fields = [
            'id', 'numero_vente', 'sale_date', 'total_amount', 
            'products_count', 'artisan_details', 'produits', 'artisan_products'
        ]
    
    def get_produits(self, obj):
        """Retourne la liste des produits disponibles pour la sélection"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
            
        # Déterminer l'artisan (soit celui de la vente, soit l'utilisateur connecté)
        artisan = None
        if obj and hasattr(obj, 'artisan') and obj.artisan:
            artisan = obj.artisan
        elif request.user.user_type == 'artisan':
            artisan = request.user.artisan_profile
        
        if not artisan:
            return []
            
        # Récupérer les produits en stock avec leurs catégories
        produits = artisan.produit_set.filter(
            stock__gt=0
        ).select_related('categorie').order_by('name')
        
        return [
            {
                'id': str(p.id),
                'name': p.name,
                'price': str(p.price),
                'stock': p.stock,
                'categorie': p.categorie.name if p.categorie else None,
                'selected': obj.lignes_vente.filter(product=p).exists() if obj else False,
                'quantite': obj.lignes_vente.get(product=p).quantity if obj and obj.lignes_vente.filter(product=p).exists() else 1
            }
            for p in produits
        ]
        
    def create(self, validated_data):
        """
        Crée une nouvelle vente avec les produits spécifiés.
        Format attendu :
        {
            "artisan": "uuid-de-l-artisan",
            "nom_du_client": "Nom du client",
            "produits_selectionnes": ["uuid-produit-1", "uuid-produit-2"],
            "quantites": {
                "uuid-produit-1": 2,
                "uuid-produit-2": 1
            }
        }
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({
                "non_field_errors": ["Authentification requise."]
            })
        
        # Vérifier que l'utilisateur est un administrateur
        if request.user.user_type not in ['admin', 'secondary_admin']:
            raise serializers.ValidationError({
                "non_field_errors": ["Seuls les administrateurs peuvent effectuer cette action."]
            })
        
        # Récupérer les données de la requête
        produits_selectionnes = self.initial_data.get('produits_selectionnes', [])
        quantites = self.initial_data.get('quantites', {})
        nom_du_client = validated_data.get('nom_du_client')
        artisan_id = validated_data.get('artisan')
        
        # Valider les données
        if not nom_du_client:
            raise serializers.ValidationError({"nom_du_client": ["Le nom du client est requis."]})
            
        if not artisan_id:
            raise serializers.ValidationError({"artisan": ["La sélection d'un artisan est requise."]})
            
        if not produits_selectionnes:
            raise serializers.ValidationError({"produits_selectionnes": ["Au moins un produit doit être sélectionné."]})
        
        # Récupérer l'artisan
        try:
            artisan = Artisan.objects.get(id=artisan_id)
        except Artisan.DoesNotExist:
            raise serializers.ValidationError({"artisan": ["Artisan introuvable."]})
        
        # Créer la vente dans une transaction
        with transaction.atomic():
            # Créer la vente
            vente = Vente.objects.create(
                artisan=artisan,
                nom_du_client=nom_du_client
            )
            
            # Créer les lignes de vente
            for produit_id in produits_selectionnes:
                try:
                    produit = Produit.objects.get(id=produit_id, artisan=artisan)
                except Produit.DoesNotExist:
                    raise serializers.ValidationError({
                        "produits_selectionnes": [f"Produit avec l'ID {produit_id} non trouvé pour cet artisan."]
                    })
                
                # Récupérer la quantité (par défaut 1 si non spécifiée)
                quantite = quantites.get(str(produit_id), 1)
                
                # Vérifier le stock
                if produit.stock < quantite:
                    raise serializers.ValidationError({
                        "quantites": [f"Stock insuffisant pour le produit {produit.name}. Stock disponible : {produit.stock}"]
                    })
                
                # Créer la ligne de vente
                LigneVente.objects.create(
                    vente=vente,
                    product=produit,
                    quantity=quantite,
                    unit_price=produit.price
                )
                
                # Mettre à jour le stock
                produit.stock -= quantite
                produit.save(update_fields=['stock'])
        
        # Recharger la vente avec les relations
        vente.refresh_from_db()
        return vente

    def validate(self, data):
        """
        Valide les données de vente.
        La validation des lignes de vente est faite dans le sérialiseur LigneVenteSerializer.
        """
        # Récupérer l'artisan (déjà validé dans to_internal_value)
        artisan = data.get('artisan')
        
        # Si l'utilisateur est un artisan, on utilise automatiquement son profil
        if not artisan and self.context['request'].user.user_type == 'artisan':
            artisan = self.context['request'].user.artisan_profile
            data['artisan'] = artisan
        
        # Vérifier qu'un artisan est défini
        if not artisan:
            raise ValidationError({
                'artisan_name': "L'artisan est requis pour effectuer une vente."
            })
        
        # Vérifier qu'il y a au moins une ligne de vente
        lignes_data = self.initial_data.get('lignes_vente', [])
        if not lignes_data:
            raise ValidationError({
                'lignes_vente': "Au moins un produit est requis pour la vente."
            })
        
        # Valider chaque ligne de vente
        for ligne_data in lignes_data:
            # Créer un sérialiseur pour valider la ligne
            ligne_serializer = LigneVenteSerializer(
                data=ligne_data,
                context={
                    'request': self.context['request'],
                    'artisan': artisan
                }
            )
            
            if not ligne_serializer.is_valid():
                raise ValidationError({
                    'lignes_vente': ligne_serializer.errors
                })
        
        return data

    def create(self, validated_data):
        """
        Crée une nouvelle vente avec plusieurs lignes de vente.
        Met à jour automatiquement les stocks des produits.
        """
        lignes_data = validated_data.pop('lignes_vente')
        user = self.context['request'].user
        
        # Pour les artisans, on utilise automatiquement leur profil
        if user.user_type == 'artisan':
            validated_data['artisan'] = user.artisan_profile
        
        # Créer la vente
        vente = Vente.objects.create(**validated_data)
        
        # Créer les lignes de vente et mettre à jour les stocks
        for ligne_data in lignes_data:
            product = ligne_data['product']
            quantity = ligne_data['quantity']
            
            # Créer la ligne de vente
            LigneVente.objects.create(
                vente=vente,
                product=product,
                quantity=quantity,
                unit_price=product.price  # Utiliser le prix actuel du produit
            )
            
            # Mettre à jour le stock
            product.stock -= quantity
            product.save(update_fields=['stock'])
        
        return vente
