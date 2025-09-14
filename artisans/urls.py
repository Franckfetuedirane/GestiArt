from rest_framework.routers import DefaultRouter
from .views import ArtisanViewSet

router = DefaultRouter()
router.register(r'artisans', ArtisanViewSet)

urlpatterns = router.urls

