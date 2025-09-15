

# produits/admin.py
from django.contrib import admin
from .models import Produit, Categorie

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation')
    search_fields = ('nom',)
    list_filter = ('date_creation',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('name', 'categorie', 'artisan', 'price', 'stock', 'date_added')
    list_filter = ('categorie', 'artisan', 'date_added')
    search_fields = ('name', 'description')
    autocomplete_fields = ['artisan']  # Pour faciliter la sélection de l'artisan

    readonly_fields = ('date_added',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'categorie', 'artisan')
        }),
        ('Détails', {
            'fields': ('price', 'stock', 'numero_boutique', 'image')
        }),
        ('Dates', {
            'fields': ('date_added',)
        }),
    )