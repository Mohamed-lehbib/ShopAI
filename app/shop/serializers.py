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


# class ProductSerializer(serializers.ModelSerializer):
#     """Serializer for products."""

#     class Meta:
#         model = Product
#         fields = ['id', 'user', 'category',
#                   'name', 'description', 'price', 'stock', 'image']
#         read_only_fields = ['id', 'user']
        
# class ProductSerializer(serializers.ModelSerializer):
#     """Serializer for products, including detailed category information."""
#     category = CategorySerializer(read_only=True)  # Use the CategorySerializer for the category field

#     class Meta:
#         model = Product
#         fields = ['id', 'user', 'category', 'name', 'description', 'price', 'stock', 'image']
#         read_only_fields = ['id', 'user']
        
class ProductSerializer(serializers.ModelSerializer):
    category_detail = serializers.SerializerMethodField(read_only=True)  # For returning the category object
    category_id = serializers.IntegerField(write_only=True, required=False)  # For accepting category ID on write

    class Meta:
        model = Product
        fields = ['id', 'user', 'category_detail', 'category_id', 'name', 'description', 'price', 'stock', 'image']
        read_only_fields = ['id', 'user', 'category_detail']  # include 'category_detail' here

    def get_category_detail(self, obj):
        """Return the category object."""
        return CategorySerializer(obj.category).data

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            validated_data['category'] = Category.objects.get(id=category_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            instance.category = Category.objects.get(id=category_id)
        return super().update(instance, validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to products."""
    image = serializers.ImageField(required=True)

    class Meta:
        model = Product
        fields = ['id', 'image']
        read_only_fields = ['id']


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


# class OrderSerializer(serializers.ModelSerializer):
#     """Serializer for the order object."""
#     products = OrderItemSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'products', 'created_at', 'updated_at']
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class OrderSerializer(serializers.ModelSerializer):
#     """Serializer for the order object."""
#     products = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
#     user_email = serializers.SerializerMethodField(read_only=True)  # Add this line to include user's email

#     class Meta:
#         model = Order
#         fields = ['id', 'user_email', 'products', 'created_at', 'updated_at']  # Replace 'user_details' with 'user_email'
#         read_only_fields = ['id', 'created_at', 'updated_at']

#     def get_user_email(self, obj):
#         """Retrieve the user's email."""
#         return obj.user.email  # Ensure your Order model has a 'user' field pointing to the User model


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating order items, expects product_id and quantity."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()



class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the order object."""
    products = serializers.ListField(
        child=OrderCreateSerializer(), write_only=True
    )
    product_details = OrderItemSerializer(source='orderitem_set', many=True, read_only=True, required=False)
    user_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_email', 'products', 'product_details', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_email', 'product_details']

    def get_user_email(self, obj):
        return obj.user.email

    def create(self, validated_data):
        products_data = validated_data.pop('orderitem_set', [])
        order = Order.objects.create(user=self.context['request'].user)

        for product_data in products_data:
            # Corrected to use 'product_id' instead of 'product'
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity')
            product = Product.objects.get(id=product_id)  # Ensure this product_id exists to avoid DoesNotExist error

            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order


