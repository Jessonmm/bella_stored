from . import views
from django.urls import path
from category.models import *
from .models import *


urlpatterns = [

    path('store/', views.store, name='store'),
    path('store/<str:category_slug>/', views.store, name='products_by_categories'),
    path('search/', views.search, name='search'),
    path('store/<slug:category_slug>/<slug:subcategory_slug>/', views.store,name='products_by_sub_categories'),
    path('product_remove/<int:product_id>/', views.cart_remove, name='product_remove'),
    path('product_update/<int:product_id>/', views.cart_update, name='product_update'),
    path('store/<slug:category_slug>/<slug:subcategory_slug>/<slug:product_slug>/', views.product_details,name='product_details'),

    ]
