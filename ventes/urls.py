from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_ui

router = DefaultRouter()
router.register(r'ventes', views_ui.VenteViewSet, basename='vente')

urlpatterns = [
    path('', include(router.urls)), 
    path('nouvelle-vente/', views_ui.create_vente_form, name='create_vente_form'),
    path('stats/', views_ui.StatsView.as_view(), name='stats'),
]
