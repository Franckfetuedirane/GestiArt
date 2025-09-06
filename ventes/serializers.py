from rest_framework import serializers
from .models import Vente
from produits.models import Produit
from artisans.models import Artisan
from produits.serializers import ProduitSerializer
from artisans.serializers import ArtisanSerializer

class VenteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Vente (Sale) model.
    Includes nested `ProductSerializer` and `ArtisanSerializer` for read-only details.
    Handles stock validation and automatic stock deduction upon sale creation.
    """
    product_details = ProduitSerializer(source='product', read_only=True)
    artisan_details = ArtisanSerializer(source='artisan', read_only=True)

    class Meta:
        """
        Meta class for VenteSerializer.
        Defines the model and fields to be serialized, and read-only fields.
        """
        model = Vente
        fields = ('id', 'product', 'product_details', 'quantity', 'unit_price', 'total_price', 'sale_date', 'artisan', 'artisan_details')
        read_only_fields = ('id', 'sale_date', 'unit_price', 'total_price', 'artisan', 'product_details', 'artisan_details')

    def validate(self, data):
        """
        Validates the sale data, ensuring quantity is positive and sufficient stock is available.
        """
        product = data['product']
        quantity = data['quantity']

        if quantity <= 0:
            raise serializers.ValidationError({'quantity': "La quantité doit être supérieure à zéro."})        
        if product.stock < quantity:
            raise serializers.ValidationError({'quantity': f"Stock insuffisant. {product.name} n'a que {product.stock} en stock."})            
        return data

    def create(self, validated_data):
        """
        Creates a new sale instance and automatically updates product stock.
        Associates the sale with the correct artisan based on user type.
        """
        product = validated_data['product']
        quantity = validated_data['quantity']
        user = self.context['request'].user

        if user.user_type == 'artisan':
            if product.artisan.user != user:
                raise serializers.ValidationError({'product': "Vous ne pouvez vendre que vos propres produits."})            
            artisan = user.artisan_profile
        else: # Admin can sell any product and associate with any artisan linked to the product
            artisan = product.artisan

        validated_data['artisan'] = artisan
        validated_data['unit_price'] = product.price

        vente = super().create(validated_data)
        product.stock -= quantity
        product.save()
        return vente
