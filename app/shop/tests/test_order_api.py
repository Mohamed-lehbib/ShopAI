"""
Tests for the Order Api.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Order,
    OrderItem,
    Product,
    Category
)
from shop.serializers import OrderSerializer

ORDERS_URL = reverse('shop:order-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_product(user, category, **params):
    """Create and return a sample product."""
    defaults = {
        'name': 'Sample product',
        'description': 'Sample product description',
        'price': 5.99,
        'stock': 10,
    }
    defaults.update(params)
    return Product.objects.create(user=user, category=category, **defaults)


class PublicOrderAPITests(TestCase):
    """Test unauthenticated order API access."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for accessing orders."""
        res = self.client.get(ORDERS_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateOrderApiTests(TestCase):
    """Test authenticated order API access."""

    def setUp(self):
        self.user = create_user(email='user@example.com', password='test123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_orders(self):
        """Test retrieving a list of orders."""
        order = Order.objects.create(user=self.user)
        category = Category.objects.create(name='Sample Category')
        OrderItem.objects.create(
            order=order,
            product=create_product(self.user, category=category)
        )

        res = self.client.get(ORDERS_URL)

        orders = Order.objects.filter(user=self.user)
        serializer = OrderSerializer(orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_order(self):
        """Test creating a new order."""
        category = Category.objects.create(name='Sample Category')
        product = create_product(user=self.user, category=category)
        payload = {
            'products': [
                {'product': product.id, 'quantity': 2}
            ]
        }

        res = self.client.post(ORDERS_URL, data=payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.get()
        self.assertEqual(order_item.product, product)
        self.assertEqual(order_item.quantity, 2)

    def test_retrieve_user_orders(self):
        """Test retrieving orders of the authenticated user."""
        # Create orders for different users
        user2 = create_user(email='user2@example.com', password='testpass123')
        order_user1 = Order.objects.create(user=self.user)
        Order.objects.create(user=user2)

        # Ensure only user's orders are retrieved
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only one order should be retrieved
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], order_user1.id)
