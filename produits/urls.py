from rest_framework.routers import DefaultRouter
from .views import ProduitViewSet, CategorieViewSet

router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'categories', CategorieViewSet, basename='categorie')

urlpatterns = router.urls
