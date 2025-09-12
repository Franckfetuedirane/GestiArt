from django.db import models
from artisans.models import Artisan
from categories.models import Category

class Produit(models.Model):
    """
    Represents a product created by an Artisan in the GestiArt application.
    Includes details like name, description, category, price, stock, associated artisan,
    and an image for the product.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    date_added = models.DateField(auto_now_add=True)
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='produits_images/', blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the product.
        """
        return self.name
