from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, serializers
from .models import Vente
from .serializers import VenteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

@login_required
def create_vente_form(request):
    """
    Vue pour afficher le formulaire de création de vente
    """
    return render(request, 'vente_form.html')

# ventes/views_ui.py
class VenteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sales to be viewed or edited.
    """
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Vente.objects.all()
        if not self.request.user.is_staff:
            # Assurez-vous que l'utilisateur a bien un profil artisan
            if hasattr(self.request.user, 'artisan_shop'):
                queryset = queryset.filter(artisan=self.request.user.artisan_shop)
            else:
                # Si l'utilisateur n'a pas de profil artisan, retournez un queryset vide
                return Vente.objects.none()
        return queryset

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'artisan_shop'):
            serializer.save(artisan=self.request.user.artisan_shop)
        else:
            # Gérer le cas où l'utilisateur n'a pas de profil artisan
            raise serializers.ValidationError("L'utilisateur n'a pas de profil artisan associé.")

class StatsView(APIView):
    def get(self, request):
        # Statistiques des ventes du mois
        start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        end_date = (start_date + timedelta(days=32)).replace(day=1)
        
        # Récupérer les ventes du mois
        ventes_du_mois = Vente.objects.filter(
            sale_date__gte=start_date,
            sale_date__lt=end_date
        )
        
        # Calculer le nombre total de ventes
        total_ventes = ventes_du_mois.count()
        
        # Calculer le montant total
        montant_total = 0
        for vente in ventes_du_mois:
            # Si vous avez une méthode pour calculer le total de la vente
            if hasattr(vente, 'calculer_total'):
                montant_total += vente.calculer_total()
            # Ou si vous avez une relation avec LigneVente
            elif hasattr(vente, 'lignes_vente'):
                montant_total += sum(ligne.sous_total for ligne in vente.lignes_vente.all() if hasattr(ligne, 'sous_total'))

        return Response({
            'total_ventes': total_ventes,
            'montant_total': montant_total,
            'periode': {
                'debut': start_date,
                'fin': end_date
            },
            'status': 'success'
        }, status=status.HTTP_200_OK)