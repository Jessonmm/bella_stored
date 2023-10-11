from . import views
from django.urls import path
from category.models import *
from .models import *


urlpatterns = [

    path('store/', views.store, name='store'),
    path('store/<str:category_slug>/', views.store, name='products_by_categories'),
    path('search/', views.search, name='search'),
    path('store/<slug:category_slug>/<slug:subcategory_slug>/', views.store,name='products_by_sub_categories'),

    path('store/<slug:category_slug>/<slug:subcategory_slug>/<slug:product_slug>/', views.product_details,name='product_details'),

    ]
