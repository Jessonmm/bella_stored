from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('dashboards/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('admin/update_order/<int:order_id>/', views.update_order, name='update_order'),
    path('orders/', views.orders, name='orders'),
    path('get_wallet/', views.get_wallet, name='get_wallet'),


    path('coupons/', views.coupons, name='coupons'),
    path('add-coupon/', views.addcoupon, name='add-coupon'),
    path('edit-coupon/', views.editcoupon, name='edit-coupon'),
    path('update-coupon/<str:coupon_id>/', views.updatecoupon, name='update-coupon'),
    path('delete-coupon/<str:coupon_id>', views.deletecoupon, name='delete-coupon'),

    path('product/', views.products, name='product'),
    path('list-product/<int:id>/',views.listproduct, name='list-product'),
    path('add-product/', views.addproduct, name='add-product'),
    path('edit-product/', views.editproduct, name='edit-product'),
    path('updated-product/<str:product_id>/', views.updateproduct, name='updated-product'),
    path('delete-product/<str:product_id>', views.deleteproduct, name='delete-product'),

    path('add-category/', views.addcategory, name='add-category'),
    path('updated-category/<str:category_id>/', views.updatedcategory, name='updated-category'),
    path('list-category/<int:id>/', views.listcategories, name='list-category'),
    path('categories/', views.categories, name='categories'),


    path('add-subcategory/', views.addsubcategory, name='add-subcategory'),
    path('list-subcategory/<int:id>/',views.list_subcategory, name='list-subcategory'),
    path('updated-subcategory/<str:subcategory_id>/', views.updatedsubcategory, name='updated-subcategory'),
    path('delete-subcategory/<str:subcategory_id>', views.deletesubcategory, name='delete-subcategory'),
    path('subcategory/', views.subcategories, name='subcategory'),
    path('delete-subcategory/', views.deletesubcategory, name='delete-subcategory'),

    path('userview', views.userview, name='userview'),
    path('delete-user/<int:id>/', views.deleteuser, name='delete-user'),
    path('block-user/<int:id>/', views.blockuser, name='block-user'),



]
