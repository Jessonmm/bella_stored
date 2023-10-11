from django.contrib import admin
from django.urls import path,include
from django.conf  import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dj-admin/', admin.site.urls),
    path('admin/', include('myadmin.urls')),
    path('', include('accounts.urls')),
    path('', include('shop.urls')),
    path('', include('cart.urls')),
    path('', include('category.urls')),
    path('', include('orders.urls')),
    path('', include('profiles.urls')),

 ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

handler404='shop.views.error_404'
