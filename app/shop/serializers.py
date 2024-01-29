"""
Serializer of shop api.
"""
from rest_framework import serializers
from core.models import (
    Category,
    Product,
    Order,
    OrderItem
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = ['id', 'user', 'category',
                  'name', 'description', 'price', 'stock']
        read_only_fields = ['id', 'user']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    product_data = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_data', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the order object."""
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
