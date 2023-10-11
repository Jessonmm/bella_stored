from django.shortcuts import render, redirect
from django.contrib import messages
from orders.models import Address
from django.db.models import Q
from .models import UserProfile
from category.models import SubCategories
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import re

from .forms import UserProfileForm


# Create your views here.

@login_required(login_url = 'login')
@never_cache
def profiles(request):

    if not request.user.is_authenticated:
        return redirect('login')
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Make sure the form's file input field is named 'profile_image'
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=userprofile)

    return render(request, 'profile/profile.html', {'form': form})



@login_required
def user_profile(request):
    pass


@login_required(login_url = 'login')
@never_cache
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user


    if request.method == 'POST':
        try:
            new_username = request.POST.get('Username', user.username)
            new_email = request.POST.get('Email', user.email)
            new_phone_number = request.POST.get('Phone_number', user.phone_number)

            if not new_username:
                messages.error(request,'username is required')
                return redirect('profiles')
            if not new_email:
                messages.error(request,'email is required')

            pattern2=r'^[a-zA-Z0-9_%-+]+@gmail\.com$'
            if not re.match(pattern2,new_email):

                messages.error(request,'email is not valid')
                return redirect('profiles')

            if not new_phone_number:
                messages.error(request,'phone number is required')
                return redirect('profiles')
            pattern = r'^\d{10}$'

            if not re.match(pattern,new_phone_number):
                messages.error(request,'phone number must  be 10 digits')
                return redirect('profiles')

            if len(set(new_phone_number))==1:
                messages.error(request,'phone number is not valid')
                return redirect('profiles')



            # Update user's fields
            user.username = new_username
            user.email = new_email
            user.phone_number = new_phone_number
            user.save()
            messages.success(request,'user profile updated successfully')
            return redirect('profiles')
        except Exception as e:
            messages.error(request,"An error occurred while updating your profile")
            return redirect('profiles')
    else:
        return redirect('profiles')




@login_required(login_url = 'login')
@never_cache
def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        old_password = request.POST['Old_password']
        new_password = request.POST['New_password']
        confirm_new_password = request.POST['Confirm_new_password']

        if not old_password:
            messages.error(request, 'old password is required')
            return redirect('change-password')
        if not new_password:
            messages.error(request, 'new password is required')
            return redirect('change-password')
        if not confirm_new_password:
            messages.error(request, 'confirm_new_password is required')
            return redirect('change-password')
        if len(new_password) <= 6:
            messages.error(request, 'New password must be at least 7 characters long')
            return redirect('change-password')


        if request.user.check_password(old_password):
            if new_password == confirm_new_password:
                if new_password != old_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Password changed successfully')
                    return redirect('change-password')
                else:
                    messages.error(request, 'New password and old password are the same')
                    return redirect('change-password')
            else:
                messages.error(request, 'New passwords do not match')
                return redirect('change-password')
        else:
            messages.error(request, 'Current password is incorrect')
            return redirect('change-password')

    return render(request, 'profile/change password.html')





@login_required(login_url = 'login')
@never_cache
def myaddress(request):
    if not request.user.is_authenticated:
        return redirect('login')
    current_user = request.user
    try:
        addresses = Address.objects.filter(user=current_user)
    except ObjectDoesNotExist:
        addresses = []

    context = {'address': addresses}
    return render(request, 'profile/myaddress.html', context)




def addaddress(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':

            user = request.user  # Get the logged-in user
            first_name = request.POST['Firstname']
            last_name = request.POST['Lastname']
            email = request.POST['Email']
            phone_number = request.POST['Phone_number']
            address_line1 = request.POST['Address1']
            address_line2 = request.POST['Address2']
            country = request.POST['Country']
            state = request.POST['State']
            district = request.POST['District']
            city = request.POST['City']
            pincode = request.POST['Pincode']
            order_note = request.POST['Ordernote']


            if not first_name:
                messages.error(request,'first name is required')
                return  redirect('add_address')
            if not last_name:
                messages.error(request,'last name is required')
                return  redirect('add_address')
            if not email:
                messages.error(request,'email is required')
                return  redirect('add_address')
            pattern1 = r'^[a-zA-Z0-9_%-+]+@gmail\.com$'
            if not re.match(pattern1, email):
                messages.error(request, 'Email is not valid')
                return redirect('add_address')
            if not phone_number:
                messages.error(request,'phone number is required')
                return  redirect('add_address')

            if len(set(phone_number))==1:
                messages.error(request,'Phone number is not valid')
                return  redirect('add_address')

            pattern = r'^\d{10}$'
            if not re.match(pattern, phone_number):
                messages.error(request, 'Phone number must had 10 numbers')
                return redirect('add_address')
            if not address_line1:
                messages.error(request,'address1 is required')
                return  redirect('add_address')
            if not address_line2:
                messages.error(request,'address2 is required')
                return  redirect('add_address')
            if not country:
                messages.error(request,'country is required')
                return  redirect('add_address')
            if not state:
                messages.error(request,'state is required')
                return  redirect('add_address')
            if not district:
                messages.error(request,'district is required')
                return  redirect('add_address')
            if not city:
                messages.error(request,'city is required')
                return  redirect('add_address')
            if not pincode:
                messages.error(request,'pincode is required')
                return  redirect('add_address')

            pattern3 = r'^\d{6}$'

            if not re.match(pattern3,pincode):
                messages.error(request,'pincode must have 6 numbers')
                return redirect('add_address')
            if len(set(pincode))==1:
                messages.error(request,'pincode is not valid')
                return redirect('add_address')
            if not order_note:
                messages.error(request,'order_note is required')
                return  redirect('add_address')

            if Address.objects.filter(first_name=first_name):
                messages.error(request,'firstname already exists')
                return redirect('add_address')
            if Address.objects.filter(last_name=last_name):
                messages.error(request,'lastname already exists')
                return redirect('add_address')
            if Address.objects.filter(email=email):
                messages.error(request,'email already exists')
                return redirect('add_address')
            if Address.objects.filter(phone_number=phone_number):
                messages.error(request,'phone_number already exists')
                return redirect('add_address')
            if Address.objects.filter(address_line1=address_line1):
                messages.error(request,'address1  already exists')
                return redirect('add_address')
            if Address.objects.filter(address_line2=address_line2):
                messages.error(request,'address2 already exists')
                return redirect('add_address')
            if Address.objects.filter(order_note=order_note):
                messages.error(request,'order_note already exists')
                return redirect('add_address')

            new_address = Address(
                user=user,  # Associate the user with the address
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                address_line1=address_line1,
                address_line2=address_line2,
                country=country,
                state=state,
                district=district,
                city=city,
                pincode=pincode,
                order_note=order_note
            )
            new_address.save()
            messages.success(request,'address added successfully')
            return redirect('my_address')

    return render(request, 'profile/add_address.html')




def editaddress(request, id):
    address = get_object_or_404(Address, id=id)
    context = {'address': address}
    return render(request, 'profile/edit_address.html', context)




def updateaddress(request, id):
        if not request.user.is_authenticated:
            return redirect('login')



        if request.method == 'POST':
            # Update the address fields
            first_name = request.POST['Firstname']
            last_name = request.POST['Lastname']
            email = request.POST['Email']
            phone_number = request.POST['Phone_number']
            address_line1 = request.POST['Address1']
            address_line2 = request.POST['Address2']
            country = request.POST['Country']
            state = request.POST['State']
            district = request.POST['District']
            city = request.POST['City']
            pincode = request.POST['Pincode']
            order_note = request.POST['Ordernote']

            if not first_name:
                messages.error(request,'first name is required')
                return  redirect('my_address')
            if not last_name:
                messages.error(request,'last name is required')
                return  redirect('my_address')
            if not email:
                messages.error(request,'email is required')
                return  redirect('my_address')
            pattern1 = r'^[a-zA-Z0-9_%-+]+@gmail\.com$'
            if not re.match(pattern1, email):
                messages.error(request, 'Email is not valid')
                return redirect('my_address')
            if not phone_number:
                messages.error(request,'phone number is required')
                return  redirect('my_address')

            if len(set(phone_number))==1:
                messages.error(request,'Phone number is not valid')
                return  redirect('my_address')

            pattern = r'^\d{10}$'
            if not re.match(pattern, phone_number):
                messages.error(request, 'Phone number must had 10 numbers')
                return redirect('my_address')
            if not address_line1:
                messages.error(request,'address1 is required')
                return  redirect('my_address')
            if not address_line2:
                messages.error(request,'address2 is required')
                return  redirect('my_address')
            if not country:
                messages.error(request,'country is required')
                return  redirect('my_address')
            if not state:
                messages.error(request,'state is required')
                return  redirect('my_address')
            if not district:
                messages.error(request,'district is required')
                return  redirect('my_address')
            if not city:
                messages.error(request,'city is required')
                return  redirect('my_address')
            if not pincode:
                messages.error(request,'pincode is required')
                return  redirect('my_address')

            pattern3 = r'^\d{6}$'

            if not re.match(pattern3,pincode):
                messages.error(request,'pincode must have 6 numbers')
                return redirect('my_address')

            if len(set(pincode))==1:
                messages.error(request,'pincode is not valid')
                return redirect('my_address')
            if not order_note:
                messages.error(request,'order_note is required')
                return redirect('my_address')

            if Address.objects.filter(first_name=first_name):
                messages.error(request,'firstname already exists')
                return redirect('my_address')
            if Address.objects.filter(last_name=last_name):
                messages.error(request,'lastname already exists')
                return redirect('my_address')
            if Address.objects.filter(email=email):
                messages.error(request,'email already exists')
                return redirect('my_address')
            if Address.objects.filter(phone_number=phone_number):
                messages.error(request,'phone_number already exists')
                return redirect('my_address')
            if Address.objects.filter(address_line1=address_line1):
                messages.error(request,'address1  already exists')
                return redirect('my_address')
            if Address.objects.filter(address_line2=address_line2):
                messages.error(request,'address2 already exists')
                return redirect('my_address')
            if Address.objects.filter(order_note=order_note):
                messages.error(request,'order_note already exists')
                return redirect('my_address')

            # Save the updated address
            address = get_object_or_404(Address, id=id)
            address.first_name=first_name
            address.last_name=last_name
            address.email=email
            address.phone_number=phone_number
            address.address_line1=address_line1
            address.address_line2=address_line2
            address.country=country
            address.state=state
            address.district=district
            address.city=city
            address.pincode=pincode
            address.order_note=order_note
            address.save()
            messages.success(request,'address updated successfully')
            return redirect('my_address')


        return redirect('my_address')




def deleteaddress(request, id):
    try:
        if not request.user.is_authenticated:
            return redirect('login')
        addresses = Address.objects.filter(id=id)
        addresses.delete()
        messages.success(request,'address deleted successfully')
        return redirect('my_address')

    except Address.DoesNotExist:
        return render(request, 'profile/profile.html.html', {'error_message': 'Address not found'})

    except Exception as e:
        error_message = str(e)
        return render(request, 'profile/profile.html.html', {'error_message': error_message})



