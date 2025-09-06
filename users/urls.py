from django.urls import path
# from rest_framework.authtoken.views import obtain_auth_token # Remove this import
from .views import RegisterView, UserListView, UserDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # path('obtain-token/', obtain_auth_token, name='obtain_auth_token'), # Remove this path
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
