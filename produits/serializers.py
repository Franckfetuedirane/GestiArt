# produits/serializers.py
from rest_framework import serializers
from .models import Produit, Categorie
from artisans.serializers import ArtisanSerializer

class ProduitSerializer(serializers.ModelSerializer):
    artisan_detail = ArtisanSerializer(source='artisan', read_only=True)
    
    class Meta:
        model = Produit
        fields = [
            'id', 'name', 'description', 'categorie', 'artisan', 'artisan_detail',
            'price', 'stock', 'numero_boutique', 'image'
        ]
        read_only_fields = ['date_added']
        extra_kwargs = {
            'categorie': {'required': True},
            'artisan': {'required': True},
            'price': {'required': True, 'min_value': 0},
            'stock': {'required': True, 'min_value': 0}
        }

    def validate_artisan(self, value):
        if not value:
            raise serializers.ValidationError("Un artisan doit être sélectionné")
        return value

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'date_creation', 'date_mise_a_jour']
        read_only_fields = ['date_creation', 'date_mise_a_jour']

