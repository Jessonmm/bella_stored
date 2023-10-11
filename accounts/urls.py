from . import views
from django.urls import path


urlpatterns = [
    path('login',views.loginPage,name='login'),
    path('logout', views.user_logout, name='logout'),
    path('',views.home,name='home'),
    path('register',views.registerPage,name='register'),
    path('otp/',views.otpuser,name='otp'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),
    path('forgot_password',views.forgot_password,name   ='forgot_password'),


]
