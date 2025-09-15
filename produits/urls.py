# from rest_framework.routers import DefaultRouter
# from .views import ProduitViewSet, CategorieViewSet
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()
# router.register(r'produits', ProduitViewSet)
# router.register(r'categories', CategorieViewSet, basename='categorie')
# router.register(r'categories', CategorieViewSet)

# urlpatterns = router.urls


from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'produits', views.ProduitViewSet, basename='produit')
router.register(r'categories', views.CategorieViewSet, basename='categorie')

urlpatterns = [
    path('', include(router.urls)),
]