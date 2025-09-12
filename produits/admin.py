from django.contrib import admin
from .models import Produit, Categorie

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'date_creation', 'date_mise_a_jour')
    search_fields = ('nom', 'description')
    list_filter = ('date_creation',)
    prepopulated_fields = {}
    ordering = ('nom',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('name', 'artisan', 'get_categorie', 'price', 'stock', 'date_added')
    search_fields = ('name', 'categorie__nom', 'artisan__first_name', 'artisan__last_name')
    list_filter = ('categorie', 'artisan', 'date_added')
    raw_id_fields = ('artisan',)
    autocomplete_fields = ('categorie',)

    def get_categorie(self, obj):
        return obj.categorie.nom if obj.categorie else "-"
    get_categorie.short_description = 'Catégorie'
