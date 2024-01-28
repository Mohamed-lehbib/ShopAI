"""
Serializer of shop api.
"""
from rest_framework import serializers
from core.models import (
    Category,
    Product
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
