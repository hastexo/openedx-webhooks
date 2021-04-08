from .views import order_create, order_delete

from django.urls import path

urlpatterns = [
    path('order/create', order_create, name='woocommerce_order_create'),
    path('order/delete', order_create, name='woocommerce_order_delete'),
]
