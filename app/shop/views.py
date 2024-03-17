"""
View for Shop Api.
"""
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS, AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from cloudinary.uploader import upload as cloudinary_upload
from core.models import (
    Category,
    Product,
    Order,
    OrderItem,
    User
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    OrderSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """View for managing categories."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('-name')

    def get_permissions(self):
        """Customize permission classes based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


@method_decorator(csrf_exempt, name='dispatch')
class ProductViewSet(viewsets.ModelViewSet):
    """View for managing products."""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Return products for the current authenticated user
          or all products if the user is a superuser."""
        # if self.request.user.is_superuser:
        #     return Product.objects.all()
        # elif self.request.user.is_authenticated:
        #     return Product.objects.filter(user=self.request.user)
        # else:
        #     return Product.objects.none()
        return Product.objects.all()

    def get_permissions(self):
        """Customize permission classes based on action and user."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.request.user.is_superuser:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # def perform_create(self, serializer):
    #     """Create a new product. Superuser can assign product to any user."""
    #     user = self.request.user if not self.request.user.is_superuser else None
    #     serializer.save(user=user)
    def perform_create(self, serializer):
        """Create a new product, ensuring only superusers can create, and optionally assign it to a specific user."""
        # Assuming you're passing an optional 'user_id' in your request to assign the product to a different user
        # Only superusers should reach this point due to the get_permissions logic for the 'create' action
        if 'user_id' in self.request.data and self.request.user.is_superuser:
            # Attempt to find the specified user and assign the product to them
            user_id = self.request.data['user_id']
            try:
                user = User.objects.get(id=user_id)  # Replace CustomUserModel with your user model
            except User.DoesNotExist:
                user = None
        else:
            # If no 'user_id' is provided, or if the requestor is not a superuser, default to the requesting user
            user = self.request.user
        
        serializer.save(user=user)


    def update(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=kwargs['pk']).first()
        if product and not request.user.is_superuser and product.user != request.user:
            return Response({'detail': 'Not authorized to update this product.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=kwargs['pk']).first()
        if product and not request.user.is_superuser and product.user != request.user:
            return Response({'detail': 'Not authorized to delete this product.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a product."""
        product = self.get_object()

        # Extract the file from the request
        file = request.FILES.get('image')
        if not file:
            return Response({'detail': 'No image provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Upload to Cloudinary
        try:
            upload_result = cloudinary_upload(
                file,
                folder='product_images',
                resource_type='image'
            )
        except Exception as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update product image URL
        product.image = upload_result['url']
        product.save()

        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """Viewset for managing orders."""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    # def perform_create(self, serializer):
    #     products_data = serializer.validated_data.pop('products')
    #     order = serializer.save(user=self.request.user)

    #     for product_data in products_data:
    #         product = product_data['product']

    #         # Check if product is a Product instance
    #         # and extract ID if necessary
    #         if isinstance(product, Product):
    #             product_id = product.id
    #         else:
    #             product_id = product

    #         quantity = product_data['quantity']

    #         # Now retrieve the product using the ID
    #         product_instance = Product.objects.get(id=product_id)

    #         if quantity > product_instance.stock:
    #             raise ValidationError(
    #                 f'Insufficient stock for product ID {product_id}.'
    #             )

    #         OrderItem.objects.create(
    #             order=order,
    #             product=product_instance,
    #             quantity=quantity
    #         )

    #         # Update product stock
    #         product_instance.stock -= quantity
    #         product_instance.save()

    @transaction.atomic
    def perform_create(self, serializer):
        products_data = serializer.validated_data.pop('products')
        order = serializer.save(user=self.request.user)

        for product_data in products_data:
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity')

            # Retrieve the product using the product_id
            try:
                product_instance = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise ValidationError({'product_id': f'Product with id {product_id} does not exist.'})

            # Check stock availability
            if quantity > product_instance.stock:
                raise ValidationError({
                    'quantity': f'Insufficient stock for product ID {product_id}. Available: {product_instance.stock}, requested: {quantity}.'
                })

            # Create OrderItem instance
            OrderItem.objects.create(
                order=order,
                product=product_instance,
                quantity=quantity
            )

            # Update product stock
            product_instance.stock -= quantity
            product_instance.save()

    def get_queryset(self):
        """Retrieve all orders for superuser, or orders for the current authenticated user."""
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()  # Superuser gets all orders
        return Order.objects.filter(user=user)  # Other users get their orders

    # def get_queryset(self):
    #     """Retrieve orders for the current authenticated user."""
    #     return Order.objects.filter(user=self.request.user)
