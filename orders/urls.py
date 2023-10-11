from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),

    path('payments/', views.payments, name='payments'),
    path('payments_completed/', views.payments_completed, name='payments_completed'),

    path('razorpay/', views.razorpay, name='razorpay'),
    path("cash_on_delivery/<str:order_number>/", views.cash_on_delivery, name='cash_on_delivery'),
    path('my-orders/', views.my_orders, name='my-orders'),
    path('order-details/<int:order_id>', views.order_details, name='order-details'),
    path("cancel_order/<int:id>/",views.cancel_order,name='cancel_order'),
    path("return_order/<int:id>/",views.return_order,name='return_order'),
    path('coupon/', views.coupon, name='coupon'),
    path('wallet/', views.wallet, name='wallet'),


]