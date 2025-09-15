# produits/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Categorie, Produit
from artisans.models import Artisan

User = get_user_model()

class ProduitTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='artisan'
        )
        self.artisan = Artisan.objects.create(
            user=self.user,
            prenom='Test',
            nom='User',
            email='test@example.com'
        )
        self.categorie = Categorie.objects.create(
            nom='Test Catégorie',
            description='Description de test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        url = '/api/produits/produits/'
        data = {
            'name': 'Produit de test',
            'description': 'Description de test',
            'categorie': self.categorie.id,
            'price': '99.99',
            'stock': 10
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produit.objects.count(), 1)
        self.assertEqual(Produit.objects.get().name, 'Produit de test')