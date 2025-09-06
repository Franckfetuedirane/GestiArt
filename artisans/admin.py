from django.contrib import admin
from .models import Artisan

@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'speciality', 'department', 'image')
    search_fields = ('first_name', 'last_name', 'speciality')
    list_filter = ('speciality', 'department')
