"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import (
    Category,
    Product,
    Order,
    OrderItem,
    Cart,
    CartItem
)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_category_with_name_successful(self):
        """Test creating a category with a name is successful."""
        name = 'Electronics'
        category = Category.objects.create(name=name)
        self.assertEqual(category.name, name)

    # Product model tests
    def test_create_product_with_details_successful(self):
        """Test creating a product with details is successful."""
        user = get_user_model().objects.create_user(
            email='productowner@example.com',
            password='testpass123'
        )
        category = Category.objects.create(name='Electronics')
        name = 'Laptop'
        description = 'High-performance laptop'
        price = 999.99
        stock = 10

        product = Product.objects.create(
            user=user,
            category=category,
            name=name,
            description=description,
            price=price,
            stock=stock
        )

        self.assertEqual(product.user, user)
        self.assertEqual(product.category, category)
        self.assertEqual(product.name, name)
        self.assertEqual(product.description, description)
        self.assertEqual(product.price, price)
        self.assertEqual(product.stock, stock)

    # Order model tests
    def test_create_order_with_user_and_products_successful(self):
        """Test creating an order with a user and products is successful."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        category = Category.objects.create(name='Electronics')
        product = Product.objects.create(
            user=user,
            category=category,
            name='Laptop',
            description='High-performance laptop',
            price=999.99,
            stock=10
        )
        order = Order.objects.create(user=user)
        OrderItem.objects.create(order=order, product=product, quantity=1)

        self.assertEqual(order.user, user)
        self.assertIn(product, order.products.all())

    # Cart model tests
    def test_create_cart_for_user_successful(self):
        """Test creating a cart for a user is successful."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        cart = Cart.objects.create(user=user)
        self.assertEqual(cart.user, user)

    def test_create_cart_item_successful(self):
        """Test creating a cart item is successful."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        category = Category.objects.create(name='Electronics')
        product = Product.objects.create(
            user=user,
            category=category,
            name='Laptop',
            description='High-performance laptop',
            price=999.99,
            stock=10
        )
        cart = Cart.objects.create(user=user)
        cart_item = CartItem.objects.create(cart=cart,
                                            product=product, quantity=2)

        self.assertEqual(cart_item.cart, cart)
        self.assertEqual(cart_item.product, product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertIn(cart_item, cart.items.all())
