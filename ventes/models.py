from django.db import models
from django.db.models import Max, Sum
from django.core.validators import MinValueValidator
from produits.models import Produit
from artisans.models import Artisan
import uuid


def generate_sale_number():
    """
    Génère un numéro de vente unique au format V-YYYYMMDD-XXXX
    où XXXX est un numéro séquentiel
    """
    from datetime import datetime
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'V-{today}'
    
    # Trouver le dernier numéro de vente pour aujourd'hui
    last_sale = Vente.objects.filter(numero_vente__startswith=prefix).order_by('-numero_vente').first()
    
    if last_sale:
        try:
            last_number = int(last_sale.numero_vente.split('-')[-1])
            next_number = last_number + 1
        except (IndexError, ValueError):
            next_number = 1
    else:
        next_number = 1
        
    return f'{prefix}-{next_number:04d}'

class LigneVente(models.Model):
    """
    Représente une ligne de vente pour un produit spécifique.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vente = models.ForeignKey(
        'Vente',
        on_delete=models.CASCADE,
        related_name='lignes_vente',
        verbose_name='Vente associée'
    )
    product = models.ForeignKey(
        'produits.Produit',
        on_delete=models.PROTECT,
        related_name='lignes_vente',
        verbose_name='Produit vendu'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantité vendue'
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Prix unitaire de vente'
    )

    class Meta:
        verbose_name = 'Ligne de vente'
        verbose_name_plural = 'Lignes de vente'
        ordering = ['-id']

    def __str__(self):
        return f'{self.quantity}x {self.product.name} - {self.unit_price}€'

    def save(self, *args, **kwargs):
        # S'assurer que le prix unitaire est bien celui du produit
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
        # Mettre à jour le stock du produit
        if self.pk:  # Si la ligne existe déjà
            old_quantity = LigneVente.objects.get(pk=self.pk).quantity
            self.product.stock += old_quantity  # On remet l'ancienne quantité
        
        # On soustrait la nouvelle quantité
        self.product.stock -= self.quantity
        self.product.save()

    def delete(self, *args, **kwargs):
        # Remettre le stock à jour avant la suppression
        self.product.stock += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)


class Vente(models.Model):
    """
    Représente une vente avec plusieurs produits.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artisan = models.ForeignKey(
        'artisans.Artisan',
        on_delete=models.PROTECT,
        related_name='ventes',
        verbose_name='Artisan vendeur'
    )
    sale_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de vente'
    )
    numero_vente = models.CharField(
        max_length=50,
        unique=True,
        default='TEMP-0000',
        verbose_name='Numéro de vente'
    )
    nom_du_client = models.CharField(
        max_length=100,
        verbose_name='Nom du client',
        help_text='Nom du client pour la vente',
        blank=True,
        null=True
    )
    
    # Champs calculés (propriétés)
    @property
    def total_amount(self):
        """Calcule le montant total de la vente."""
        return self.lignes_vente.aggregate(
            total=Sum(models.F('quantity') * models.F('unit_price'))
        )['total'] or 0
    
    @property
    def products_count(self):
        """Retourne le nombre de produits différents dans la vente."""
        return self.lignes_vente.count()

    def generate_sale_number(self):
        """
        Génère un numéro de vente unique au format V-YYYYMMDD-XXXX
        où XXXX est un numéro séquentiel
        """
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        prefix = f'V-{today}'
        
        # Trouver le dernier numéro de vente pour aujourd'hui
        last_sale = Vente.objects.filter(
            numero_vente__startswith=prefix
        ).order_by('-numero_vente').first()
        
        if last_sale:
            try:
                last_number = int(last_sale.numero_vente.split('-')[-1])
                next_number = last_number + 1
            except (IndexError, ValueError):
                next_number = 1
        else:
            next_number = 1
            
        return f'{prefix}-{next_number:04d}'

    def save(self, *args, **kwargs):
        """Sauvegarde la vente en générant un numéro unique si nécessaire."""
        is_new = self._state.adding
        if is_new and not self.numero_vente:
            self.numero_vente = self.generate_sale_number()
        super().save(*args, **kwargs)

    def get_artisan_details(self):
        """Retourne les détails de l'artisan pour la facturation."""
        return {
            'id': self.artisan.id,
            'nom': self.artisan.nom,
            'prenom': self.artisan.prenom,
            'email': self.artisan.user.email if hasattr(self.artisan, 'user') else None,
            'telephone': self.artisan.telephone,
            'adresse': self.artisan.adresse,
            'numero_boutique': self.artisan.numero_boutique
        }

    def get_products_details(self):
        """Retourne les détails des produits pour la facturation."""
        return [{
            'id': ligne.product.id,
            'nom': ligne.product.name,
            'description': ligne.product.description,
            'prix_unitaire': float(ligne.unit_price),
            'quantite': ligne.quantity,
            'sous_total': float(ligne.quantity * ligne.unit_price),
            'numero_boutique': ligne.product.numero_boutique,
            'image': ligne.product.image.url if ligne.product.image else None
        } for ligne in self.lignes_vente.select_related('product').all()]

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-sale_date']

    def __str__(self):
        """Représentation textuelle de la vente."""
        return f"{self.numero_vente} - {self.products_count} produits - {self.total_amount}€"
