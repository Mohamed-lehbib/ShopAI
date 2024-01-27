"""
Test for the category api.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Category
from shop.serializers import CategorySerializer

CATEGORIES_URL = reverse('shop:category-list')


def detail_url(category_id):
    """Create and return a category detail URL."""
    return reverse('shop:category-detail', args=[category_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicCategoryApiTests(TestCase):
    """Test unauthenticated category API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_categories_unauthenticated(self):
        """Test listing categories without authentication."""
        Category.objects.create(name='Electronics')
        Category.objects.create(name='Books')

        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_category_unauthenticated(self):
        """Test retrieving a single category without authentication."""
        category = Category.objects.create(name='Electronics')
        url = detail_url(category.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_category_authenticated_required(self):
        """Test that creating a category requires authentication."""
        payload = {'name': 'New Category'}
        res = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateCategoryApiTests(TestCase):
    """Test authenticated category API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        """Test retrieving a list of categories."""
        Category.objects.create(name='Electronics')
        Category.objects.create(name='Books')

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_successful(self):
        """Test creating a new category."""
        payload = {'name': 'Toys'}
        self.client.post(CATEGORIES_URL, payload)

        exists = Category.objects.filter(
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_update_category(self):
        """Test updating a category."""
        category = Category.objects.create(name='Groceries')

        payload = {'name': 'Supermarket'}
        url = detail_url(category.id)
        self.client.patch(url, payload)

        category.refresh_from_db()
        self.assertEqual(category.name, payload['name'])

    def test_delete_category(self):
        """Test deleting a category."""
        category = Category.objects.create(name='Games')

        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
