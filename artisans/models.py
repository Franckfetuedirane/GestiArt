from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import os

def artisan_photo_path(instance, filename):
    """
    Génère le chemin de stockage pour la photo de l'artisan.
    """
    # Utilisez le nom de l'utilisateur pour éviter les conflits
    filename = os.path.basename(filename)
    return f"artisans/{instance.user.username}/{filename}"

class Artisan(models.Model):
    """
    Modèle représentant un artisan.
    """
    id = models.AutoField(primary_key=True)  # S'assurer que c'est présent

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='artisan_shop'  # Changed to avoid conflict with ArtisanProfile
    )
    numero_boutique = models.CharField(
        _('Numéro de boutique'),
        max_length=50,
        unique=True,
        help_text=_('Numéro unique identifiant la boutique de l\'artisan')
    )
    prenom = models.CharField(
        _('Prénom'),
        max_length=100
    )
    nom = models.CharField(
        _('Nom'),
        max_length=100
    )
    telephone = models.CharField(
        _('Téléphone'),
        max_length=20
    )
    email = models.EmailField(
        _('Email de contact'),
        blank=True,
        null=True
    )
    adresse = models.TextField(
        _('Adresse'),
        blank=True,
        null=True,
        help_text=_('Adresse complète de l\'artisan')
    )
    specialite = models.CharField(
        _('Spécialité'),
        max_length=100,
        help_text=_('Spécialité principale de l\'artisan')
    )
    
    photo = models.ImageField(
        _('Photo de profil'),
        upload_to=artisan_photo_path,
        blank=True,
        null=True,
        help_text=_('Photo de profil de l\'artisan')
    )


    date_inscription = models.DateTimeField(
        _('Date d\'inscription'),
        auto_now_add=True
    )
    actif = models.BooleanField(
        _('Actif'),
        default=True,
        help_text=_('Désactiver pour masquer l\'artisan sans supprimer ses données')
    )


    def __str__(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        verbose_name = _('Artisan')
        verbose_name_plural = _('Artisans')

    @property
    def nom_complet(self):
        """Retourne le nom complet de l'artisan."""
        return f"{self.prenom} {self.nom}"

    @property
    def total_ventes(self):
        """Retourne le montant total des ventes de l'artisan."""
        from django.db.models import Sum, F
        from ventes.models import Vente
        
        total = Vente.objects.filter(artisan=self).aggregate(
            total=Sum(F('lignes_vente__quantity') * F('lignes_vente__unit_price'))
        )['total'] or 0
        
        return total

    @property
    def nombre_produits_vendus(self):
        """Retourne le nombre total de produits vendus par l'artisan."""
        from django.db.models import Sum
        from ventes.models import Vente
        
        total = Vente.objects.filter(artisan=self).aggregate(
            total=Sum('lignes_vente__quantity')
        )['total'] or 0
        
        return total