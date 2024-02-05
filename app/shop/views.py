"""
View for Shop Api.
"""
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
# from rest_framework.parsers import MultiPartParser, FormParser
# from drf_spectacular.utils import extend_schema
from core.models import (
    Category,
    Product,
    Order,
    OrderItem
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
    queryset = Product.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Return products for the current authenticated user
          or all products."""
        if self.request.user.is_authenticated:
            return Product.objects.filter(user=self.request.user)
        return Product.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'upload_image':
            return ProductImageSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        """Create a new product."""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=kwargs['pk']).first()
        if product and product.user != request.user:
            return Response(
                {'detail': 'Not authorized to update this product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=kwargs['pk']).first()
        if product and product.user != request.user:
            return Response(
                {'detail': 'Not authorized to delete this product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    # @extend_schema(request={'multipart/form-data': ProductImageSerializer})
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a product."""
        product = self.get_object()
        serializer = self.get_serializer(
            product,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    """Viewset for managing orders."""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        products_data = serializer.validated_data.pop('products')
        order = serializer.save(user=self.request.user)

        for product_data in products_data:
            product = product_data['product']

            # Check if product is a Product instance
            # and extract ID if necessary
            if isinstance(product, Product):
                product_id = product.id
            else:
                product_id = product

            quantity = product_data['quantity']

            # Now retrieve the product using the ID
            product_instance = Product.objects.get(id=product_id)

            if quantity > product_instance.stock:
                raise ValidationError(
                    f'Insufficient stock for product ID {product_id}.'
                )

            OrderItem.objects.create(
                order=order,
                product=product_instance,
                quantity=quantity
            )

            # Update product stock
            product_instance.stock -= quantity
            product_instance.save()

    def get_queryset(self):
        """Retrieve orders for the current authenticated user."""
        return Order.objects.filter(user=self.request.user)
