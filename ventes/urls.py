from rest_framework.routers import DefaultRouter
from .views import VenteViewSet

router = DefaultRouter()
router.register(r'ventes', VenteViewSet)

urlpatterns = router.urls
