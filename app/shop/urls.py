"""
URL mapping for the shop app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('orders', views.OrderViewSet)

app_name = 'shop'

urlpatterns = [
    path('', include(router.urls)),
]
