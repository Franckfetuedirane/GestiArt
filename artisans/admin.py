# from django.contrib import admin
# from .models import Artisan

# @admin.register(Artisan)
# class ArtisanAdmin(admin.ModelAdmin):
#     list_display = ('user', 'first_name', 'last_name', 'speciality', 'department', 'image')
#     search_fields = ('first_name', 'last_name', 'speciality')
#     list_filter = ('speciality', 'department')

# artisans/admin.py
from django.contrib import admin
from .models import Artisan

@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ('numero_boutique', 'prenom', 'nom', 'specialite', 'telephone', 'actif')
    list_filter = ('specialite', 'actif', 'date_inscription')
    search_fields = ('numero_boutique', 'nom', 'prenom', 'email')
    ordering = ('nom', 'prenom')
    readonly_fields = ('date_inscription',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'prenom', 'nom', 'email', 'telephone')
        }),
        ('Informations professionnelles', {
            'fields': ('numero_boutique', 'specialite', 'adresse')
        }),
        ('Statut', {
            'fields': ('actif', 'date_inscription')
        }),
    )