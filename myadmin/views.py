from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.shortcuts import render,redirect,get_object_or_404
from  django.contrib.auth import  authenticate,login,logout
from django.db.models.functions import TruncMonth,TruncYear
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from  django.contrib import messages
from  accounts.models import Account
from datetime import date,datetime
from django.core.paginator import Paginator
from django.utils import timezone
from category.models import  *
from  orders.models import *
from shop.models import  *
import json
# Create your views here.




@staff_member_required(login_url = 'admin_login')
def dashboard(request):

    # Find the earliest created_at month in your data
    earliest_month = Order.objects.earliest('created_at').created_at
    start_year = earliest_month.year

    # Generate labels starting from the earliest year
    labeled = []
    current_year = start_year

    for _ in range(12):
        labeled.append(str(current_year))
        current_year += 1

    # Generate labels starting from the earliest month
    labels = []
    current_month = earliest_month.replace(day=1)  # Set day to 1 to ensure the start of the month
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    for _ in range(12):
        labels.append(month_names[current_month.month - 1] + " " + str(current_month.year))
        current_month = current_month.replace(day=1, month=(current_month.month % 12) + 1)
        if current_month.month == 1:
            current_month = current_month.replace(year=current_month.year + 1)

    # Query to retrieve monthly product sales data
    monthly_product_sales = Order.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_sales=Sum(ExpressionWrapper(F('order_total'), output_field=DecimalField()))
    ).order_by('month')

    # Create a dictionary to store monthly sales with formatted date labels
    monthly_sales_data = {
        entry['month'].strftime('%b %Y'): entry['total_sales']
        for entry in monthly_product_sales
    }

    yearly_sales = Order.objects.annotate(
        year=TruncYear('created_at')
    ).values('year').annotate(
        total_yearly_sales=Sum(ExpressionWrapper(F('order_total'), output_field=DecimalField()))
    ).order_by('year')

    yearly_sales_data = {
        entry['year'].strftime('%Y'): entry['total_yearly_sales']
        for entry in yearly_sales
    }

    orders=Order.objects.all()
    order_count=orders.count()

    total_quantity=Order.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity']or 0
    total_price=Order.objects.aggregate(total_price=Sum('order_total'))['total_price'] or 0
    accounts=Account.objects.all()
    account_count=accounts.count()
    total_sales_by_date= Order.objects.values('created_at__date').annotate(total_sales=Sum('order_total')).annotate(total_quantity_in_day=Sum('quantity'))

    paginator = Paginator(total_sales_by_date, per_page=3)
    page_number = request.GET.get('page', 1)
    page_total_sales_by_date= paginator.get_page(page_number)

    current_year=date.today().year

    total_sales_by_month= Order.objects.values('created_at__month').annotate(total_sales=Sum('order_total')).annotate(total_quantity_in_month=Sum('quantity'))

    paginator = Paginator(total_sales_by_month, per_page=3)
    page_number = request.GET.get('page', 1)
    page_total_sales_by_month = paginator.get_page(page_number)

    total_sales_by_year= Order.objects.values('created_at__year').annotate(total_sales=Sum('order_total')).annotate(total_quantity_in_year=Sum('quantity'))

    paginator = Paginator(total_sales_by_year, per_page=3)
    page_number = request.GET.get('page', 1)
    page_total_sales_by_year = paginator.get_page(page_number)

    this_products = Products.objects.all()


    order_product_quantities={}

    for this_product in this_products:
        total_quantity_for_product=OrderProduct.objects.filter(product=this_product).aggregate(total_quantity_is=Sum('quantity'))['total_quantity_is'] or 0
        order_product_quantities[this_product.product_name]=total_quantity_for_product

    top_sold_products=sorted(order_product_quantities.items(),key=lambda x:x[1],reverse=True)[:3]

    # Convert top_sold_products to JSON
    top_sold_products_json = json.dumps(top_sold_products)

    top_selling_products = OrderProduct.objects.values('product__product_name').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold')[:10]

    today=datetime.today()
    today_date = today.strftime("%Y-%m-%d")
    today_sale_count=Order.objects.filter(created_at__date=today_date).count()

    month_names = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }

    for entry in total_sales_by_month:
        entry['month_name'] = month_names.get(entry['created_at__month'])




    context={
             'top_selling_product':top_selling_products,
             'total_sales_by_date':page_total_sales_by_date,
             'total_sales_by_month':page_total_sales_by_month,
             'total_sales_by_year':page_total_sales_by_year,
             'account_count':account_count,
             'order_count':order_count,
             'quantity':total_quantity,
             'total_price':total_price,
             'monthly_product_sales':monthly_product_sales,
              'monthly_sales_data':monthly_sales_data,
              'labels':labels,
              'labeled':labeled,
              'yearly_sales_data': yearly_sales_data,
              'top_sold_products':top_sold_products,
               'top_sold_products_json': top_sold_products_json,
              'today_sale_count':today_sale_count,


    }

    return  render(request,'admin side/dashboard.html',context)



@staff_member_required(login_url = 'admin_login')
def get_wallet(request):
    wallet=Wallet.objects.all().order_by('user')

    paginator = Paginator(wallet, per_page=4)
    page_number = request.GET.get('page', 1)
    page_wallet = paginator.get_page(page_number)
    context = {
        'wallet':page_wallet
    }
    return render(request, 'admin side/get_wallet.html', context)



@staff_member_required(login_url = 'admin_login')
def update_order(request, order_id):
    try:
        if request.method == 'POST':
            order = get_object_or_404(Order, id=order_id)
            status = request.POST.get('status')
            order.status = status
            messages.success(request,'order is updated')
            order.save()



            if status == "Delivered":
                try:
                    payment = Payment.objects.get(payment_id=order.order_number, status=False)
                    if payment.payment_method == 'Cash On Delivery':
                        payment.status = True
                        payment.save()
                        messages.success(request, "Payment marked as completed for Cash On Delivery order.")
                except Payment.DoesNotExist :
                    messages.warning(request, "No pending payment found for this order.")
                    return redirect('orders')
                messages.success (request, 'order updated successfully')
                return ('orders')

    except Exception as e:
        error_message = str(e)
        messages.error(request, f"Error: {error_message}")

    return redirect('orders')



@staff_member_required(login_url = 'admin_login')
def profile(request):
    return  render(request,'admin side/profiles.html')


@staff_member_required(login_url = 'admin_login')
def coupons(request):

    coupons=Coupons.objects.all().order_by('code')
    paginator=Paginator(coupons,per_page=4)
    page_number=request.GET.get('page',1)
    page_coupon=paginator.get_page(page_number)

    try:
        context = {
            'coupons': page_coupon
        }
    except Exception as e:
        error_message = str(e)
        messages.error(request, f"Error: {error_message}")
        return render(request, 'admin_side/coupons.html', {'coupons': []})

    return render(request, 'admin side/coupons.html', context)


@staff_member_required(login_url = 'admin_login')
def addcoupon(request):
    if request.method == 'POST':
        try:
            code = request.POST['Code']
            discount = request.POST['Discount']
            min_value = request.POST['Min_Value']
            valid_at = request.POST['Valid_At']
            active = request.POST['Active']

            if not code:
                messages.error(request,'code is required')
                return redirect('coupons')
            if not discount:
                messages.error(request,'discount is required')
                return redirect('coupons')
            if not min_value:
                messages.error(request,'min value is required')
                return redirect('coupons')
            if not valid_at:
                messages.error(request,'valid_at is required')
                return redirect('coupons')
            if  not active:
                messages.error(request,'active is required')
                return redirect('coupons')
            if Coupons.objects.filter(code=code):
                messages.error(request,'code already exists')
                return render('coupons')


            coupon = Coupons(
                code=code,
                discount=discount,
                min_value=min_value,
                valid_at=valid_at,
                active=active,
            )

            coupon.save()
            messages.success(request, 'Coupon added successfully')
            return redirect('coupons')

        except Exception as e:

            return redirect('coupons')

    return render(request, 'admin side/coupons.html')





@staff_member_required(login_url = 'admin_login')
def editcoupon(request):
    try:
        coupons = Coupons.objects.all()
        context = {
            'coupons': coupons
        }
        return render(request, 'admin_side/coupons.html')

    except Exception as e:
        error_message = str(e)
        context = {
            'error_message': error_message
        }
        return render(request, 'admin side/coupons.html', context)



@staff_member_required(login_url = 'admin_login')
def updatecoupon(request, coupon_id):
    if request.method == 'POST':
        try:
            code = request.POST['Code']
            discount = request.POST['Discount']
            min_value = request.POST['Min_Value']
            valid_at = request.POST['Valid_At']
            active = request.POST['Active']

            if not code:
                messages.error(request,'code is required')
                return redirect('coupons')
            if not discount:
                messages.error(request,'discount is required')
                return redirect('coupons')
            if not min_value:
                messages.error(request,'min value is required')
                return redirect('coupons')
            if not valid_at:
                messages.error(request,'valid_at is required')
                return redirect('coupons')
            if  not active:
                messages.error(request,'active is required')
                return redirect('coupons')

            coupon = Coupons.objects.get(id=coupon_id)
            coupon.code=code
            coupon.discount=discount
            coupon.min_value=min_value
            coupon.valid_at=valid_at
            coupon.active=active
            coupon.save()
            messages.success(request, 'Coupon updated successfully')
            return redirect('coupons')

        except Exception as e:

            return redirect('coupons')

    return render(request, 'admin side/coupons.html')




@staff_member_required(login_url = 'admin_login')
def deletecoupon(request, coupon_id):
    try:
        coupon = Coupons.objects.get(id=coupon_id)
        coupon.delete()
        messages.success(request, 'Coupon deleted successfully.')
    except Coupons.DoesNotExist:
        messages.error(request, 'Coupon not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('coupons')



@staff_member_required(login_url = 'admin_login')
def orders(request):
    order=Order.objects.filter(is_ordered=True).order_by('-id')

    paginator = Paginator(order, per_page=4)
    page_number = request.GET.get('page', 1)
    page_order = paginator.get_page(page_number)
    context={'order':page_order}
    return render(request,'admin side/orders.html',context)




@staff_member_required(login_url='admin_login')
def update_order(request, order_id):
    try:
        if request.method == 'POST':
            order = get_object_or_404(Order, id=order_id)
            status = request.POST.get('status')
            order.status = status
            order.save()

            if status == "Delivered":
                try:
                    payment = Payment.objects.get(payment_id=order.order_number, status=False)
                    if payment.payment_method == 'Cash On Delivery':
                        payment.status = True
                        payment.save()
                        messages.success(request, "Payment marked as completed for Cash On Delivery order.")
                except Payment.DoesNotExist:
                    messages.warning(request, "No pending payment found for this order.")

            # Display a success message for order update
            messages.success(request, 'Order is updated successfully')

            return redirect('orders')

    except Exception as e:
        error_message = str(e)
        messages.error(request, f"Error: {error_message}")

    return redirect('orders')



@staff_member_required(login_url = 'admin_login')
def profile(request):
    return  render(request,'admin side/profiles.html')



@staff_member_required(login_url = 'admin_login')
def categories(request):
    categories = Categories.objects.all()

    paginator = Paginator(categories, per_page=4)
    page_number = request.GET.get('page', 1)
    page_categories = paginator.get_page(page_number)
    context={
        'categories': page_categories
    }
    return render(request,'admin side/category.html',context)


@staff_member_required(login_url = 'admin_login')
def addcategory(request):
    if request.method == 'POST':
        name = request.POST['Name']
        category_offer=request.POST['Category_offer']
        description = request.POST['Description']
        if not name:
            messages.error(request,'category name is required')
            return redirect('categories')
        if not category_offer:
            messages.error(request,'category offer is required')
            return redirect('categories')
        if not description:
            messages.error(request,'description is required')
            return redirect('categories')
        if Categories.objects.filter(name=name):
            messages.error(request,'category already exists')
            return  redirect('categories')



        categories=Categories(
            name=name,
            description=description,
            category_offer=category_offer,

        )
        messages.success(request,'category added successfully')
        categories.save()
        return  redirect('categories')

    return render(request,'admin side/category.html')



@staff_member_required(login_url = 'admin_login')
def editcategory(request):
    categories = Categories.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'admin side/category.html', context)


@staff_member_required(login_url = 'admin_login')
def updatedcategory(request, category_id):
    if request.method == 'POST':
        name = request.POST['Name']
        category_offer=request.POST['Category_offer']
        description = request.POST['Description']

        if not name:
            messages.error(request,'category name is required')
            return redirect('categories')
        if not category_offer:
            messages.error(request,'category offer is required')
            return redirect('categories')
        if not description:
            messages.error(request,'description is required')
            return redirect('categories')
        if Categories.objects.filter(name=name):
            messages.error(request,'category already exists')
            return  redirect('categories')

        category = Categories.objects.get(id=category_id)
        category.name=name
        category.category_offer=category_offer
        category.description=description
        messages.success(request,'category updated sucessfully')
        category.save()
        return redirect('categories')
    else:
        return redirect('categories')



def listcategories(request,id):
    categories = Categories.objects.get(id=id)
    if categories.is_listed:
        categories.is_listed=False
        categories.save()
        messages.success(request, 'category unlisted')

        return  redirect('categories')
    else:
        categories.is_listed=True
        categories.save()
        messages.success(request, 'category listed')

        return  redirect('categories')



@staff_member_required(login_url = 'admin_login')
def subcategories(request):
    subcategories = SubCategories.objects.all()
    paginator = Paginator(subcategories, per_page=4)
    page_number = request.GET.get('page', 1)
    page_subcategories = paginator.get_page(page_number)
    context = {
        'subcategories': page_subcategories
    }

    return render(request,'admin side/subcategory.html',context)



@staff_member_required(login_url='admin_login')
def addsubcategory(request):
    if request.method == 'POST':
        name = request.POST['Name']
        category_name = request.POST['Category']
        description = request.POST['Description']

        if not name:
            messages.error(request, 'Subcategory name is required')
            return redirect('subcategory')
        if not category_name:
            messages.error(request, 'Category name is required')
            return redirect('subcategory')
        if not description:
            messages.error(request, 'Description is required')
            return redirect('subcategory')
        if SubCategories.objects.filter(name=name):
            messages.error(request, 'Subcategory already exists')
            return redirect('subcategory')
        try:
            category_instance = Categories.objects.get(name=category_name)
        except Categories.DoesNotExist:
            messages.error(request, 'Category does not exist')
            return redirect('subcategory')



        subcategories = SubCategories(
            name=name,
            category=category_instance,
            description=description
        )

        subcategories.save()
        messages.success(request, 'Subcategory added successfully')
        return redirect('subcategory')

    return render(request, 'admin side/subcategory.html')



@staff_member_required(login_url = 'admin_login')
def editsubcategory(request):
    subcategories = SubCategories.objects.all()
    context = {
        'subcategories': subcategories
    }
    return render(request, 'admin side/subcategory.html', context)


@staff_member_required(login_url = 'admin_login')
def updatedsubcategory(request, subcategory_id):
    if request.method == 'POST':
        name = request.POST['Name']
        category_name=request.POST['Category']
        description = request.POST['Description']


        if not name:
            messages.error(request, 'Subcategory name is required')
            return redirect('subcategory')
        if not category_name:
            messages.error(request, 'Category name is required')
            return redirect('subcategory')
        if not description:
            messages.error(request, 'Description is required')
            return redirect('subcategory')
        if SubCategories.objects.filter(name=name):
            messages.error(request, 'Subcategory already exists')
            return redirect('subcategory')
        try:
            category_instance = Categories.objects.get(name=category_name)
        except Categories.DoesNotExist:
            messages.error(request, 'Category does not exist')
            return redirect('subcategory')


        subcategory = SubCategories.objects.get(id=subcategory_id)
        subcategory.name=name
        subcategory.category=category_instance
        subcategory.description=description
        messages.success(request,'subcategory updated successfully')
        subcategory.save()
        return redirect('subcategory')
    else:
        return redirect('subcategory')



@staff_member_required(login_url='admin_login')
def deletesubcategory(request, subcategory_id):
    try:
        subcategory = SubCategories.objects.get(id=subcategory_id)
        subcategory.delete()
        messages.success(request, 'Subcategory deleted successfully')
    except SubCategories.DoesNotExist:
        messages.error(request, 'Subcategory does not exist')

    return redirect('subcategory')



def list_subcategory(request,id):
    subcategories = SubCategories.objects.get(id=id)

    if subcategories.is_available:
        subcategories.is_available = False
        subcategories.save()
        messages.success(request, 'subcategory is unlisted')
        return redirect('subcategory')
    else:
        subcategories.is_available = True
        subcategories.save()
        messages.success(request, 'subcategory is listed')
        return redirect('subcategory')



@staff_member_required(login_url = 'admin_login')
def products(request):
    products = Products.objects.all()
    paginator = Paginator(products, per_page=4)
    page_number = request.GET.get('page',1)
    page_products = paginator.get_page(page_number)

    context={
        'products':page_products

    }
    return  render(request,'admin side/products.html',context)


def listproduct(request,id):
    products=Products.objects.get(id=id)

    if products.is_available:
        products.is_available=False
        products.save()
        messages.success(request,'product is unlisted')
        return redirect('product')
    else:
        products.is_available=True
        products.save()
        messages.success(request,'product is listed')
        return redirect('product')

@staff_member_required(login_url = 'admin_login')
def addproduct(request):
    if request.method == 'POST':
        products_name = request.POST.get('Name')
        category_name = request.POST.get('Category')
        subcategory_name = request.POST.get('Subcategory')
        price = request.POST.get('Price')
        stock = request.POST.get('Stock')
        image_1 = request.FILES.get('Image1')
        image_2 = request.FILES.get('Image2')
        image_3 = request.FILES.get('Image3')
        image_4 = request.FILES.get('Image4')
        image_5 = request.FILES.get('Image5')
        description = request.POST.get('Description')


        if not products_name:
            messages.error(request,'product name is required')
            return redirect('product')
        if not category_name:
            messages.error(request,'category name is required')
            return redirect('product')
        if not subcategory_name:
            messages.error(request,'subcategory name is required')
            return redirect('product')
        if not price:
            messages.error(request,'price is required')
            return redirect('product')
        if not stock:
            messages.error(request,'stock is required')
            return redirect('product')
        if not image_1:
            messages.error(request,'image1 is required')
            return redirect('product')
        if not image_2:
            messages.error(request,'image2 is required')
            return redirect('product')
        if not image_3:
            messages.error(request,'image3 is required')
            return redirect('product')
        if not image_4:
            messages.error(request,'image4 is required')
            return redirect('product')
        if not image_5:
            messages.error(request,'image5 is required')
            return redirect('product')
        if not description:
            messages.error(request,'description name is required')
            return redirect('product')
        if Products.objects.filter(product_name=products_name):
            messages.error('product already exists')
            return redirect('product')

        try:
            try:
                category_instance = Categories.objects.get(name=category_name)
            except Categories.DoesNotExist:
                messages.error(request,'Category does not exists')
                return redirect('product')

            try:
                subcategory_instance = SubCategories.objects.get(name=subcategory_name)
            except SubCategories.DoesNotExist:
                messages.error(request,'SubCategory does not exists')
                return redirect('product')

            new_product = Products(
                product_name=products_name,
                category_name=category_instance,
                subcategory_name=subcategory_instance,
                price=price,
                stock=stock,
                description=description,
                image_1=image_1,
                image_2=image_2,
                image_3=image_3,
                image_4=image_4,
                image_5=image_5,
            )
            messages.success(request,'product added successfully')
            new_product.save()
            return redirect('product')

        except Categories.DoesNotExist:
            messages.error(request, "Selected category does not exist.")

    categories = Categories.objects.all()
    subcategories = SubCategories.objects.all()
    return render(request, 'admin side/products.html', {'categories': categories, 'subcategories': subcategories})


@staff_member_required(login_url = 'admin_login')
def editproduct(request):
    context={
        'products':Products.objects.all()
    }
    return  render(request,'admin side/products.html',context)




@staff_member_required(login_url = 'admin_login')
def updateproduct(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':

        product_name = request.POST.get('Name')
        category_name = request.POST.get('Category')
        subcategory_name = request.POST.get('Subcategory')
        price = request.POST.get('Price')
        stock = request.POST.get('Stock')
        image_1 = request.FILES.get('Image1')
        image_2 = request.FILES.get('Image2')
        image_3 = request.FILES.get('Image3')
        image_4 = request.FILES.get('Image4')
        image_5 = request.FILES.get('Image5')
        description = request.POST.get('Description')

        try:
            try:
                category_instance = Categories.objects.get(name=category_name)
            except Categories.DoesNotExist:
                messages.error(request, 'Category does not exists')
                return redirect('product')

            try:
                subcategory_instance = SubCategories.objects.get(name=subcategory_name)
            except SubCategories.DoesNotExist:
                messages.error(request, 'SubCategory does not exists')
                return redirect('product')



            product.name =  product_name
            product.category_name = category_instance
            product.subcategory_name = subcategory_instance
            product.price = price
            product.stock = stock
            product.description = description


            if 'Image1' in request.FILES:
                product.image_1 = image_1
            if 'Image2' in request.FILES:
                product.image_2 = image_2
            if 'Image3' in request.FILES:
                product.image_3 = image_3
            if 'Image4' in request.FILES:
                product.image_4 = image_4
            if 'Image5' in request.FILES:
                product.image_5 = image_5
            messages.success(request,'product updated successfully')
            product.save()
            return redirect('product')

        except Categories.DoesNotExist:
            messages.error(request, "Selected category does not exist.")


    categories = Categories.objects.all()
    subcategories = SubCategories.objects.all()
    return render(request, 'admin side/update_product.html', {'product': product, 'categories': categories, 'subcategories': subcategories})


@staff_member_required(login_url = 'admin_login')
def deleteproduct(request,product_id):
    products= Products.objects.get(id=product_id)
    messages.success(request,'product deleted successfully')
    products.delete()
    return redirect('product')



@staff_member_required(login_url = 'admin_login')
def userview(request):
    users=Account.objects.all().order_by('username')
    paginator=Paginator(users,4)
    page_number=request.GET.get('page',1)
    page_users=paginator.get_page(page_number)
    return render(request,'admin side/userview.html',{'users':page_users})



@staff_member_required(login_url = 'admin_login')
def deleteuser(request, id):
    try:
        user = Account.objects.get(id=id)
        user.delete()
        messages.success(request,'user deleted successfully')
        return redirect('userview')  # Redirect to the 'userview' URL
    except Account.DoesNotExist:
        # Handle the case when the user with the given ID does not exist
        # For example, you can show an error message or redirect to an error page
        return redirect('userview')  # You may want to pass an error message in the redirect


@staff_member_required(login_url = 'admin_login')
def blockuser(request, id):
    user = Account.objects.get(id=id)
    if user.is_active:
        user.is_active=False
        user.save()
    else:
        user.is_active=True
        user.save()
    if user.is_active:
        messages.success(request, 'User is unblocked')
    else:
        messages.success(request, 'User is blocked')

    return redirect('userview')


def admin_login(request):
    if 'admin_username' in request.session:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']


        # Authenticate the admin user
        user = authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            # Log in the admin user
            login(request, user)
            request.session['admin_username'] = username
            messages.success(request, 'Admin login successful')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')

    return render(request, 'admin side/admin_login.html')



@staff_member_required(login_url='admin_login')
@never_cache
def admin_logout(request):
    del request.session['admin_username']
    logout(request)
    messages.success(request, 'Admin logged out successfully')
    return redirect('admin_login')