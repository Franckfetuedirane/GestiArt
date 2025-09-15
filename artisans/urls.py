from rest_framework.routers import DefaultRouter
from .views import ArtisanViewSet, get_artisans_list
from django.urls import path

router = DefaultRouter()
router.register(r'artisans', ArtisanViewSet)

# urlpatterns = router.urls

urlpatterns = [
    path('artisans/list/', get_artisans_list, name='artisans-list'),
] + router.urls