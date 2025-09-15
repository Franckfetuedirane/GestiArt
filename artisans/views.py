from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Artisan
from .serializers import ArtisanSerializer
from users.permissions import IsAdminUser, IsSecondaryAdminUser, IsAdminOrArtisanOwner
from users.models import User
from rest_framework import serializers
# artisans/views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Artisan
from .serializers import ArtisanSerializer
from users.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Artisan
from .serializers import ArtisanSerializer
from users.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

# artisans/views.py
class ArtisanViewSet(viewsets.ModelViewSet):
    queryset = Artisan.objects.all()
    serializer_class = ArtisanSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        # Si un user_id est fourni, récupérer l'utilisateur
        user_id = data.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                data['user'] = user.id  # Utiliser l'ID au lieu de l'objet
            except User.DoesNotExist:
                return Response(
                    {"error": "L'utilisateur spécifié n'existe pas."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Vérifier si l'utilisateur est admin
        is_admin = request.user.is_staff or request.user.is_superuser
        
        # Si l'utilisateur n'est pas admin, vérifier s'il a déjà un profil artisan
        if not is_admin and user_id and Artisan.objects.filter(user_id=user_id).exists():
            return Response(
                {"error": "Un artisan existe déjà pour cet utilisateur."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        return {'request': self.request}

# Déplacez cette fonction en dehors de la classe
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_artisans_list(request):
    """
    Retourne la liste de tous les artisans
    """
    artisans = Artisan.objects.all()
    serializer = ArtisanSerializer(artisans, many=True)
    return Response(serializer.data)