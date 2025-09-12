from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category
from users.models import User

class CategoryAPITests(APITestCase):
    """
    Tests for the Category API.
    """

    def setUp(self):
        # Create an admin user for authenticated requests
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword',
            user_type='admin'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create a sample category
        self.category = Category.objects.create(name='Vannerie', description='Handwoven baskets and more.')

    def test_create_category(self):
        """
        Ensure we can create a new category.
        """
        url = reverse('category-list')
        data = {'name': 'Pottery', 'description': 'Handmade clay pots.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(id=response.data['id']).name, 'Pottery')

    def test_list_categories(self):
        """
        Ensure we can list categories.
        """
        url = reverse('category-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.category.name)

    def test_get_category(self):
        """
        Ensure we can retrieve a single category.
        """
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_update_category(self):
        """
        Ensure we can update a category.
        """
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        data = {'name': 'Updated Vannerie', 'description': 'All kinds of woven goods.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Vannerie')

    def test_delete_category(self):
        """
        Ensure we can delete a category.
        """
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_category(self):
        """
        Ensure unauthenticated users cannot create a category.
        """
        self.client.logout()
        url = reverse('category-list')
        data = {'name': 'Forbidden Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
