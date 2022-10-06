from django.urls import path
from .views import (
    home, add_to_cart, remove_from_cart, decrease_quantity, increase_quantity,
    ItemDetailView, ProductAdded, CartView, CheckoutView, PaymentView, RequestRefundView, OrdersView)
app_name = 'core'



urlpatterns = [

    path('', home, name="home"),

    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('product/<slug:slug>/', ItemDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('product-added/<slug>/', ProductAdded.as_view(), name='product-added'),
    path('decrease-quantity/<slug>/', decrease_quantity, name='decrease-quantity'),
    path('increase-quantity/<slug>/', increase_quantity, name='increase-quantity'),
    path('cart/', CartView.as_view(), name='cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

    path('orders/', OrdersView.as_view(), name='orders'),

]


