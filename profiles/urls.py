from . import views
from django.urls import path


urlpatterns = [

    path('profiles/',views.profiles,name='profiles'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('edit-profile/',views.edit_profile,name='edit-profile'),
    path('change-password/',views.change_password,name='change-password'),
    path('myadd_address_address/', views.myaddress, name='my_address'),
    path('add_address/', views.addaddress, name='add_address'),
    path('edit_address/<int:id>/',views.editaddress,name="edit_address"),
    path('update_address/<int:id>',views.updateaddress,name="update_address"),
    path('delete_address/<int:id>',views.deleteaddress,name="delete_address"),



]
