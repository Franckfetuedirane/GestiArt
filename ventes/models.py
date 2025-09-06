from django.db import models
from produits.models import Produit
from artisans.models import Artisan
import uuid

class Vente(models.Model):
    """
    Represents a sale transaction in the GestiArt application.
    Automatically generates a unique ID, links to a Product and an Artisan,
    and calculates the total price.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='sales')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    artisan = models.ForeignKey(Artisan, on_delete=models.PROTECT, related_name='sales')

    def save(self, *args, **kwargs):
        """
        Overrides the save method to set the unit_price from the product's price if not already set.
        """
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """
        Calculates the total price for the sale.
        """
        return self.quantity * self.unit_price

    def __str__(self):
        """
        Returns a string representation of the sale.
        """
        return f"Vente {self.id} - {self.product.name} ({self.quantity})"
