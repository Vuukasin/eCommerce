from django.urls import path
from .views import (
    home, add_to_cart, remove_from_cart, decrease_quantity, increase_quantity, mice_view, keyboard_view, components_view, laptops_view, audio_view, streaming_view,
    chairs_view, console_view, new_items_view, last_chance_view, exclusives_view,
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



    # Label 
    path('gaming-mice/', mice_view, name='gaming-mice'),
    path('gaming-keyboards/', keyboard_view, name='gaming-keyboards'),
    path('components/', components_view, name='components'),
    path('gaming-laptops/', laptops_view, name='gaming-laptops'),
    path('gaming-audio/', audio_view, name='gaming-audio'),
    path('gaming-chairs/', chairs_view, name='gaming-chairs'),
    path('streaming/', streaming_view, name='streaming'),
    path('console-gaming/', console_view, name='console-gaming'),

    path('new/', new_items_view, name='new'),
    path('last-chance/', last_chance_view, name='last-chance'),
    path('exclusives/', exclusives_view, name='exclusives'),
]


