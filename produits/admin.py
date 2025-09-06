from django.contrib import admin
from .models import Produit

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('name', 'artisan', 'category', 'price', 'stock', 'date_added', 'image')
    search_fields = ('name', 'category', 'artisan__first_name', 'artisan__last_name')
    list_filter = ('category', 'artisan', 'date_added')
    raw_id_fields = ('artisan',)
