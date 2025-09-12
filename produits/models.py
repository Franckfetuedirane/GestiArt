from django.db import models
from artisans.models import Artisan

class Categorie(models.Model):
    """
    Représente une catégorie de produits dans l'application GestiArt.
    Chaque catégorie a un nom et une description.
    """
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Produit(models.Model):
    """
    Represents a product created by an Artisan in the GestiArt application.
    Includes details like name, description, category, price, stock, associated artisan,
    and an image for the product.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='produits',
        verbose_name="Catégorie"
    )
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
