
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.db.models import Q

from django.core.mail import send_mail
from django.contrib import messages
from category.models import  *
from accounts.models import Account
from django.conf import settings
import smtplib

import string
import random
import base64
import pyotp
import re


def home(request):
    categories=Categories.objects.all()
    return render(request, 'accounts/home.html',{'categories':categories})



def generate_secret_key():
    try:
        secret_key_length = 16
        characters = string.ascii_letters + string.digits
        secret_key = ''.join(random.choice(characters) for _ in range(secret_key_length))
        return secret_key
    except Exception as e:
        error_message = str(e)
        return 'Error: ' + error_message


def generate_otp(secret_key):
    try:
        otp = pyotp.TOTP(secret_key)
        otp_value = otp.now()
        return otp_value
    except Exception as e:
        error_message = str(e)
        return 'Error: ' + error_message

@never_cache
def otpuser(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user_otp = request.POST['otp']
        try:
            stored_otp = str(request.session['otp'])
            if user_otp == stored_otp:
                del request.session['otp']
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP')
                return redirect('otp')
        except KeyError:
            messages.error(request, 'Session expired or OTP not generated')
            return redirect('otp')

    return render(request, 'accounts/otp.html')


@never_cache
def resend_otp(request):


    if 'otp' in request.session:
        # Generate and send a new OTP
        secret_key_encoded = base64.b32encode(request.session['secret_key'].encode()).decode()
        new_otp_value = generate_otp(secret_key_encoded)
        request.session['otp'] = new_otp_value

        # Send the new OTP to the user's email
        email = request.session['email']  # Assuming you stored the email in the session during registration
        subject = 'Resend OTP Verification'
        message = f'Your new OTP is: {new_otp_value}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'New OTP sent successfully.')
        except smtplib.SMTPException as e:
            messages.error(request, 'Failed to send OTP. Please try again later.')

    return redirect('otp')


@never_cache
def registerPage(request):

        if request.user.is_authenticated:
            return redirect('home')
        if request.method == 'POST':
            username = request.POST['Username']
            phone_number = request.POST['Phone']
            email = request.POST['Email']
            password = request.POST['Password']
            password1 = request.POST['Password1']

            if not username:
                messages.error(request, 'Username is required')
                return redirect('register')

            if not re.match(r'^[A-Za-z0-9@#$%^&+=]*$', username):
                messages.error(request, 'username is not valid.')
                return redirect('register')


            if len(set(username))==1:
                messages.error(request,'username is not valid')
                return redirect('register')



            if not phone_number:
                messages.error(request, 'Phone number is required')
                return redirect('register')

            pattern=r'^\d{10}$'
            if not  re.match(pattern,phone_number):
                messages.error(request,'Phone number  is not valid')
                return redirect('register')

            if len(set(phone_number)) == 1:
                messages.error(request, 'phone number is not valid')
                return redirect('register')

            if not email:
                messages.error(request, 'Email is required')
                return redirect('register')

            pattern1=r'^[.a-zA-Z0-9_%-+]+@gmail\.com$'

            if not re.match(pattern1,email):
                messages.error(request,'Email is not valid')
                return redirect('register')


            if not password:
                messages.error(request,'password is required')
                return redirect('register')
            if not password1:
                messages.error(request,'password is required')
                return redirect('register')

            if password != password1:
                messages.error(request, 'Passwords do not match')
                return redirect('register')

            if not re.match(r'^[A-Za-z0-9@#$%^&+=]*$', password):
                messages.error(request, 'password is not valid.')
                return redirect('register')

            if not re.match(r'^[A-Za-z0-9@#$%^&+=]*$', password1):
                messages.error(request, 'password is not valid.')
                return redirect('register')

            if len(set(password))==1:
                messages.error(request,'password is not valid')
                return redirect('register')

            if len(password)<=6:
                messages.error(request,'Password must had 7 digits')
                return redirect('register')

            if len(password1)<=6:
                messages.error(request,'Passwords must had 6 digits')
                return redirect('register')



            if Account.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')

            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('register')

            if (len(set(phone_number))) == 1:
                messages.error(request, 'Phone number is not valid')
                return redirect('register')

            if Account.objects.filter(phone_number=phone_number).filter(~Q(username=username)).exists():
                messages.error(request, 'Phone number already exists')
                return redirect('register')

            secret_key = generate_secret_key()
            secret_key_encoded = base64.b32encode(secret_key.encode()).decode()
            otp_value = generate_otp(secret_key_encoded)



            request.session['otp'] = otp_value

            subject = 'OTP Verification'
            message = f'Your OTP is: {otp_value}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]



            try:
                send_mail(subject, message, from_email, recipient_list)
            except smtplib.SMTPException as e:
                messages.error(request, 'Failed to send verification email. Please try again later.')
                return redirect('register')

            request.session['secret_key'] = secret_key_encoded
            request.session['otp'] = otp_value
            request.session['email'] = email

            # Create user
            my_user = Account.objects.create_user(username=username, email=email, phone_number=phone_number, password=password)
            my_user.is_superuser = False
            my_user.is_active = True
            my_user.save()

            messages.success(request, 'User created successfully. Please verify your OTP.')
            return redirect('otp')

        return render(request, 'accounts/register.html')




def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if not email:
            messages.error(request, 'Email is required')
            return redirect('forgot_password')

        pattern1 = r'^[.a-zA-Z0-9_%-+]+@gmail\.com$'

        if not re.match(pattern1, email):
            messages.error(request, 'Email is not valid')
            return redirect('forgot_password')
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
            return redirect('forgot_password')

        # Generate password reset token
        token = default_token_generator.make_token(user)

        # Send password reset email to the user
        subject = 'Reset Your Password'
        message = f'Please click the link below to reset your password:\n\n{request.build_absolute_uri("/reset_password/")}?email={email}&token={token}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'Password reset email sent. Please check your email for further instructions.')
        except smtplib.SMTPException as e:
            messages.error(request, 'Failed to send password reset email. Please try again later.')

        return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        token = request.GET.get('token')

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, 'Invalid password reset link.')
            return redirect('forgot_password')

        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Invalid password reset link.')
            return redirect('forgot_password')

        # Store the email and token in the session for password update
        request.session['reset_email'] = email
        request.session['reset_token'] = token

        return render(request, 'accounts/reset_password.html')

    elif request.method == 'POST':
        email = request.session.get('reset_email')
        token = request.session.get('reset_token')

        if email is None or token is None:
            messages.error(request, 'Invalid password reset link.')
            return redirect('forgot_password')

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, 'Invalid password reset link.')
            return redirect('forgot_password')

        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Invalid password reset link.')
            return redirect('forgot_password')

        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Custom password validation
        if not password2:
            messages.error(request, 'password is required')
            return redirect('reset_password')

        if not password1:
            messages.error(request, 'password is required')
            return redirect('reset_password')

        if len(password1) < 6 or len(password2) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('reset_password')


        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')


        elif len(set(password1)) == 1:
            messages.error(request, 'Password is not valid.')
            return redirect('reset_password')

        elif not re.match(r'^[A-Za-z0-9@#$%^&+=]*$', password1):
            messages.error(request, 'Password is not valid.')
            return redirect('reset_password')

        else:
            # Update the user's password
            user.set_password(password1)
            user.is_superuser = False
            user.is_active = True
            user.save()

            messages.success(request, 'Password reset successful. You can now login with your new password.')
            return redirect('login')

        return redirect('reset_password')

    return redirect('forgot_password')




@never_cache
def loginPage(request):
    if 'user_username'in request.session:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']

        try:
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                request.session['user_username']=username
                messages.success(request, 'Login successful')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')
        except Exception as e:
                messages.error(request, 'An error occurred during login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
@never_cache
def user_logout(request):
    logout(request)
    messages.success(request, 'User logged out successfully')
    return redirect('home')