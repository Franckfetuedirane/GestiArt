from django.contrib import admin
from .models import Vente

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'artisan', 'quantity', 'unit_price', 'total_price', 'sale_date')
    search_fields = ('product__name', 'artisan__first_name', 'artisan__last_name')
    list_filter = ('sale_date', 'artisan', 'product__category')
    raw_id_fields = ('product', 'artisan')
    readonly_fields = ('total_price',)
