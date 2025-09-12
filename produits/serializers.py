from rest_framework import serializers
from .models import Produit, Categorie
from artisans.models import Artisan
from artisans.serializers import ArtisanSerializer

class ProduitSerializer(serializers.ModelSerializer):
    """
    Serializer for the Produit model.
    Includes nested ArtisanSerializer for read-only artisan details
    and a writable `artisan_id` field for product creation/update.
    Also includes custom validations for `stock` and `price`.
    """
    artisan = ArtisanSerializer(read_only=True)
    artisan_id = serializers.PrimaryKeyRelatedField(queryset=Artisan.objects.all(), source='artisan', write_only=True, required=False)

    class Meta:
        """
        Meta class for ProduitSerializer.
        Defines the model and fields to be serialized, and read-only fields.
        """
        model = Produit
        fields = ['id', 'name', 'description', 'categorie', 'price', 'stock', 'artisan', 'artisan_id', 'date_added', 'image']
        read_only_fields = ['id', 'date_added']

    def validate_stock(self, value):
        """
        Validates that the stock value is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Le stock ne peut pas être négatif.")
        return value

    def validate_price(self, value):
        """
        Validates that the price value is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à zéro.")
        return value


class CategorieSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Categorie.
    Permet de sérialiser et désérialiser les catégories.
    """
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'date_creation', 'date_mise_a_jour']
        read_only_fields = ['id', 'date_creation', 'date_mise_a_jour']
