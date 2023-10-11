from django.urls import path
from . import views

urlpatterns = [
    # Cart views
    path('cart/', views.cart, name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.cart_remove, name='cart_remove'),
    path('update_cart/<int:product_id>/<int:cart_item_id>/',views.cart_update,name='cart_update'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_cart_item,name='remove_cart_item'),


    path('checkout/', views.checkout, name='checkout'),




]