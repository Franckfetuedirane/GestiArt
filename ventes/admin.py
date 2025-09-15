from django.contrib import admin
from django.utils.html import format_html
from .models import Vente, LigneVente

class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1
    raw_id_fields = ('product',)
    readonly_fields = ('sous_total',)
    
    def sous_total(self, obj):
        return obj.quantity * obj.unit_price if obj.unit_price else 0
    sous_total.short_description = 'Sous-total'
    @property
    def montant_ligne(self):
       return self.quantite * self.prix_unitaire

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('numero_vente', 'artisan_display', 'designation', 'products_count', 'total_amount', 'sale_date')
    search_fields = ('numero_vente', 'designation', 'artisan__nom', 'artisan__prenom')
    list_filter = ('sale_date', 'artisan')
    raw_id_fields = ('artisan',)
    readonly_fields = ('numero_vente', 'total_amount', 'sale_date')
    inlines = [LigneVenteInline]
    
    def artisan_display(self, obj):
        return f"{obj.artisan.prenom} {obj.artisan.nom}"
    artisan_display.short_description = 'Artisan'
    artisan_display.admin_order_field = 'artisan__nom'
    
    def products_count(self, obj):
        return obj.products_count
    products_count.short_description = 'Nb. Produits'
    products_count.admin_order_field = 'lignes_vente__count'
    @property
    def total_amount(self):
        return sum(ligne.montant_ligne for ligne in self.lignes_vente.all())
    def total_amount(self, obj):
        return f"{obj.total_amount:.2f} FCFA"
    total_amount.short_description = 'Montant Total'
    total_amount.admin_order_field = 'total_amount'
    def clean(self):
       for ligne in self.lignes_vente.all():
         if ligne.quantite > ligne.produit.stock:
            raise ValidationError(
                f"Stock insuffisant pour {ligne.produit.name}. "
                f"Stock disponible : {ligne.produit.stock}"
            )