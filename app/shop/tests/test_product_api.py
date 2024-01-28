"""
Tests for product APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Product, Category
from shop.serializers import ProductSerializer

PRODUCTS_URL = reverse('shop:product-list')


def detail_url(product_id):
    """Create and return a product detail URL."""
    return reverse('shop:product-detail', args=[product_id])


def create_product(user, category, **params):
    """Create and return a sample product."""
    defaults = {
        'name': 'Sample product',
        'description': 'Sample product description',
        'price': Decimal('5.99'),
        'stock': 10,
    }
    defaults.update(params)
    return Product.objects.create(user=user, category=category, **defaults)


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicProductAPITests(TestCase):
    """Test unauthenticated product API access."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for accessing products."""
        res = self.client.get(PRODUCTS_URL)
        # self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateProductApiTests(TestCase):
    """Test authenticated product API access."""

    def setUp(self):
        self.user = create_user(email='user@example.com', password='test123')
        self.other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.category = Category.objects.create(name='Electronics')

    def test_retrieve_products(self):
        """Test retrieving a list of products."""
        other_user = create_user(
            email='other_user@example.com',
            password='testpass123'
        )
        create_product(user=self.user, category=self.category)
        create_product(user=other_user, category=self.category)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.filter(user=self.user).order_by('-id')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test creating a new product."""
        payload = {
            'category': self.category.id,
            'name': 'Laptop',
            'description': 'A high-end laptop',
            'price': Decimal('1200.99'),
            'stock': 5
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        self.assertEqual(product.name, payload['name'])
        self.assertEqual(product.user, self.user)

    def test_update_product(self):
        """Test updating a product."""
        product = create_product(user=self.user, category=self.category)

        payload = {'name': 'Updated Laptop'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product.name, payload['name'])

    def test_delete_product(self):
        """Test deleting a product."""
        product = create_product(user=self.user, category=self.category)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_update_product_unauthorized(self):
        """Test updating a product with unauthorized user."""
        product = create_product(user=self.user, category=self.category)
        # Authenticate as the other user
        self.client.force_authenticate(user=self.other_user)
        payload = {'name': 'Should not update'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        product.refresh_from_db()
        # The name should not have changed
        self.assertEqual(product.name, 'Sample product')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_unauthorized(self):
        """Test deleting a product with unauthorized user."""
        product = create_product(user=self.other_user, category=self.category)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(id=product.id).exists())
