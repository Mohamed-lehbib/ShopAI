"""
View for Shop Api.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from core.models import (
    Category,
    Product
)
from .serializers import (
    CategorySerializer,
    ProductSerializer
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
