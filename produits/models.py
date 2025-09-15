


# produits/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from artisans.models import Artisan


class Categorie(models.Model):
    nom = models.CharField(_('Nom'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    date_creation = models.DateTimeField(_('Date de création'), auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(_('Dernière mise à jour'), auto_now=True)

    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Produit(models.Model):
    name = models.CharField(_('Nom'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='produits',
        verbose_name=_('Catégorie')
    )
    price = models.DecimalField(
        _('Prix'),
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.IntegerField(
        _('Quantité en stock'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    numero_boutique = models.CharField(
        _('Numéro de boutique'),
        max_length=50, 
        blank=True, 
        null=True
    )
    date_added = models.DateField(_('Date d\'ajout'), auto_now_add=True)
    artisan = models.ForeignKey(
        'artisans.Artisan',
        on_delete=models.CASCADE,
        related_name='produits',
        verbose_name='Artisan'
    )
    image = models.ImageField(
        _('Image'),
        upload_to='produits_images/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['-date_added']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['categorie']),
            models.Index(fields=['artisan']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.stock < 0:
            raise ValueError("Le stock ne peut pas être négatif")
        super().save(*args, **kwargs)