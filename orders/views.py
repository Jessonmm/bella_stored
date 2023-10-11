from django.shortcuts import render, get_object_or_404, redirect
from cart.models import Cart, CartItem
from razorpay.errors import BadRequestError
from django.core.exceptions import ObjectDoesNotExist
from  .models import *
from shop.models import Products, Variation
from django.contrib import messages
from orders.models import Address
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import pytz
from django.contrib import messages
from django.conf import settings
import datetime
from django.http import JsonResponse
import razorpay
import json
from django.db.models import Sum

# Rest of your code

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
client =razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_KEY))
# Create your views here.



def wallet(request):
    try:
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        if created:
            wallet.save()
    except Wallet.DoesNotExist:
        wallet = None
    user=request.user
    context={'wallet':wallet, 'user':user}
    return render(request,'orders/wallet.html',context)


def  add_fund(request):
    return  redirect('wallet')


@login_required(login_url = 'accounts/login')
@never_cache
def place_order(request, total=0, quantity=0):
    if not request.user.is_authenticated:
        return redirect('login')
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    address = Address.objects.filter(user=current_user)

    if cart_count <= 0:
        return redirect('store')

    if not address:
        messages.error(request, 'Add address to place the order')
        return redirect('checkout')

    grand_total = 0
    total_quantity=0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.price * cart_item.quantity)
        quantity += cart_item.quantity

    total_quantity+=quantity
    coupon_discount = 0
    discount=0
    tax = round(int((5 * total) / 100))
    shipping = round(int((2 * total) / 100))

    if shipping <= 18:
        shipping = 0
    elif shipping > 18 and shipping <= 35:
        shipping = 35
    else:
        shipping = round(int((2 * total) / 100))
    grand_total = int(tax + total + shipping)

    if request.method == 'POST':
        coupon_code = request.POST['coupon']
        id = request.POST['flexRadioDefault']
        address = Address.objects.get(user=request.user, id=id)
        cart_item=CartItem.objects.get(user=request.user)
        data = Order()
        data.user = current_user
        data.first_name = address.first_name
        data.last_name = address.last_name
        data.phone_number = address.phone_number
        data.email = address.email
        data.address_line1 = address.address_line1
        data.address_line2 = address.address_line2
        data.state = address.state
        data.district = address.district
        data.city = address.city
        data.pincode = address.pincode
        data.order_note = address.order_note
        data.order_total = grand_total



        data.tax = tax
        data.full_price=cart_item.full_price
        data.shipping=shipping
        data.quantity=total_quantity
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        # Set the timezone to Indian Standard Time
        ist = pytz.timezone('Asia/Kolkata')

        # Get the current time in IST
        current_time = datetime.datetime.now(ist)

        # Extract the year, month, and day from the current time
        yr = int(current_time.strftime('%Y'))
        mt = int(current_time.strftime('%m'))
        dt = int(current_time.strftime('%d'))

        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")

        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()



        try:
            instance = UserCoupon.objects.get(user=request.user, coupon__code=coupon_code)

            if float(grand_total) >= float(instance.coupon.min_value):
                coupon_discount = round((float(grand_total) * float(instance.coupon.discount)) / 100)
                data.order_discount=round(coupon_discount)
                data.save()
                grand_total = int(grand_total) - coupon_discount
                print(grand_total)



            data.full_total = round(grand_total)
            print(data.order_discount)
            print(data.order_total)


            data.save()




        except ObjectDoesNotExist:

            msg = 'Invalid coupon code.'

        except Exception as e:

            msg = f'An error occurred: {str(e)}'


        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'total_quantity':total_quantity,
            'coupon_discount': coupon_discount,
            'grand_total': grand_total,
            'order_number': order_number,
            'coupon_code': coupon_code,
            'shipping':shipping,
        }

        return render(request, 'orders/payment.html', context)
    else:
        return redirect('checkout')


@login_required(login_url = 'accounts/login')
@never_cache
def cash_on_delivery(request, order_number):
    try:
        if not request.user.is_authenticated:
            return redirect('login')
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

        cart_items = CartItem.objects.filter(user=request.user)
        order.is_ordered = True

        payment = Payment(
            user=request.user,
            payment_id=order.order_number,
            order_id=order.order_number,
            payment_method='Cash On Delivery',
            amount_paid=order.order_total,
            status=False,
        )
        payment.save()

        order.payment = payment
        order.save()

        sub_total = 0  # Initialize subtotal

        for cart_item in cart_items:
            order_product = OrderProduct(
                order=order,
                user=request.user,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                product_price=cart_item.product.offer_price(),
                ordered=True,
            )
            order_product.save()

            # Assuming variations and stock updates should be done here
            order_product.variations.set(Variation.objects.all())
            order_product.save()

            product = Products.objects.get(id=cart_item.product_id)
            product.stock -= cart_item.quantity
            product.save()

            # Calculate subtotal in the loop
            sub_total += round(order_product.quantity * order_product.product_price)

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()
        ordered_product=OrderProduct.objects.filter(order_id=order.id)


        tax = round(int((5 * sub_total) / 100))
        shipping = round(int((2 * sub_total) / 100))

        if shipping <= 18:
            shipping = 0
        elif shipping > 18 and shipping <= 35:
            shipping = 35
        else:
            shipping = round(int((2 * sub_total) / 100))
        grand_total = int(tax + sub_total + shipping)
        discount=int(order.order_discount)

        context={

            'order':order,
            'sub_total':sub_total,
            'shipping':shipping,
            'grand_total':grand_total,
            'discount':discount,


            'ordered_products':ordered_product,
            'payment':payment,

        }
        return render(request, 'orders/cod_success.html',context)
    except ObjectDoesNotExist:
        messages.error(request,'The order you are trying to access does not exist.')
        return redirect('home')


@login_required(login_url = 'accounts/login')
@never_cache
def payments(request):

        body = json.loads(request.body)

        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
        payment = Payment(
            user=request.user,
            payment_id=body['transID'],
            order_id=order.order_number,
            payment_method=body['paymode'],
            amount_paid=order.order_total,
            status=True
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)

        for cart_item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = request.user.id
            order_product.product_id = cart_item.product_id
            order_product.quantity = cart_item.quantity
            order_product.product_price = cart_item.price
            order_product.ordered = True
            order_product.save()

            cart_item = CartItem.objects.get(id=cart_item.id)
            product_variation = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()

            product = Products.objects.get(id=cart_item.product_id)
            product.stock -= cart_item.quantity
            product.save()

        # clear cart
        CartItem.objects.filter(user=request.user).delete()

        # send order number and Transaction id to Web page using

        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id
        }
        return JsonResponse(data)


@login_required(login_url = 'accounts/login')
@never_cache
def payments_completed(request):
        if not request.user.is_authenticated:
            return redirect('login')
        order_number = request.GET.get('order_number')
        transID = request.GET.get('payment_id')
        try:
            order = Order.objects.get(order_number=order_number)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            payment = Payment.objects.get(payment_id=transID)

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
                'transID': payment.payment_id,
                'payment': payment,
                'subtotal': subtotal,
            }
            return render(request, 'orders/payment-success.html', context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')


@login_required(login_url = 'accounts/login')
@never_cache
def razorpay(request):

        body = json.loads(request.body)
        amount = body['amount']

        amount = float(amount) * 100

        DATA = {
            "amount": amount,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "key1": "value3",
                "key2": "value2"
            }
        }
        payment = client.order.create(data=DATA)
        return JsonResponse({
            'payment': payment,
            'payment_method': "RazerPay"
        })



@login_required(login_url = 'accounts/login')
@never_cache
def my_orders(request):
    try:
        if not request.user.is_authenticated:
            return redirect('login')
        orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
        context={'orders':orders}
        return render(request,'orders/myorders.html',context)
    except ObjectDoesNotExist:
        messages.error(request, 'An error occurred while fetching your orders.')
        return redirect('home')



@login_required(login_url = 'accounts/login')
@never_cache
def order_details(request,order_id):
    try:
        if not request.user.is_authenticated:
            return redirect('login')
        order_details = OrderProduct.objects.filter(order__order_number=order_id)
        order = Order.objects.get(order_number=order_id)
        total = 0
        for i in order_details:
            total += i.product_price * i.quantity-1
        tax = round(int((5 * total) / 100))
        shipping = round(int((2 * total) / 100))

        if shipping <= 18:
            shipping = 0
        elif shipping > 18 and shipping <= 35:
            shipping = 35
        else:
            shipping = round(int((2 * total) / 100))

        coupon_discount = 0
        grand_total = int(total + tax + shipping)
        grand_total = format(grand_total, '.2f')
        context = {
            'order_details': order_details,
            'order': order,
            'subtotal': total,
            'tax':tax,
            'shipping':shipping,
            'grand_total':grand_total
        }
        return render(request,'orders/orderdetails.html',context)
    except ObjectDoesNotExist:
        messages.error(request, 'The order details you are trying to access do not exist.')
        return redirect('home')


@login_required(login_url = 'accounts/login')
@never_cache
def cancel_order(request, id):
    try:
        if request.user.is_superadmin:
            order = Order.objects.get(order_number=id)
        else:
            order = Order.objects.get(order_number=id, user=request.user)

        payment = Payment.objects.get(order_id=order.order_number)
        order_products=OrderProduct.objects.filter(order=order)
        user=order.user
        wallet,created=Wallet.objects.get_or_create(user=user)



        if payment.payment_method == "Cash On Delivery":
            order.status = "Cancelled"
            for order_product in order_products:
                product=order_product.product
                product.stock+=order_product.quantity
                order_product.quantity=0
                order_product.save()
                product.save()
            messages.error(request,'order cancelled successfully')
            order.save()
            payment.status = False
            payment.save()
        elif payment.payment_method == "RazerPay":
            order.status ='Cancelled'
            for order_product in order_products:
                product=order_product.product
                product.stock+=order_product.quantity
                order_product.quantity=0
                order_product.save()
                product.save()
            messages.error(request,'order cancelled successfully')
            order.save()
            wallet.balance += float(payment.amount_paid)
            wallet.save()
            payment.status = False
            payment.save()

        if request.user.is_superadmin:
            return redirect('my-orders')
        else:
            return redirect('my-orders')
    except ObjectDoesNotExist:
        messages.error(request, 'The order details you are trying to access do not exist.')
        return redirect('my-orders')




def return_order(request, id):
    if request.method == 'POST':
        return_reason = request.POST['return_reason']

    if request.user.is_superuser:  # Fixed typo 'is_superadmin' to 'is_superuser'
        order = Order.objects.get(order_number=id)
    else:
        order = Order.objects.get(order_number=id, user=request.user)

    order_products = OrderProduct.objects.filter(order=order)

    for order_product in order_products:
        product = order_product.product
        product.stock += order_product.quantity
        order_product.quantity = 0
        order_product.save()
        product.save()

    order.status = 'Returned'
    order.is_returned = True
    user = order.user
    wallet, created = Wallet.objects.get_or_create(user=user)
    order.return_reason = return_reason
    messages.error(request, 'Order returned successfully')
    order.save()

    payment = Payment.objects.get(order_id=order.order_number)

    if payment.payment_method == 'Cash On Delivery':
        payment.status = False
        wallet.balance += float(payment.amount_paid)
        wallet.save()
        payment.save()
    elif payment.payment_method == 'RazerPay':
        payment.status = False
        wallet.balance += float(payment.amount_paid)
        wallet.save()
        payment.save()

    if request.user.is_superuser:
        return redirect('my-orders')
    else:
        return redirect('my-orders')


@login_required(login_url = 'accounts/login')
@never_cache
def coupon(request):
    if request.method == 'POST':
        try:
            coupon_code = request.POST['coupon']
            grand_total = request.POST['grand_total']
            coupon_discount = 0

            try:
                instance = UserCoupon.objects.get(user=request.user, coupon__code=coupon_code)

                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = (float(grand_total) * float(instance.coupon.discount)) / 100
                    grand_total = float(grand_total) - coupon_discount
                    grand_total = format(grand_total, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    msg = 'Coupon Applied successfully'
                    instance.used = True
                    instance.save()
                else:
                    msg = f'This coupon is only applicable for orders more than ₹{instance.coupon.min_value} only!'
            except UserCoupon.DoesNotExist:
                msg = 'Invalid coupon code'

            response = {
                'grand_total': grand_total,
                'msg': msg,
                'coupon_discount': coupon_discount,
                'coupon_code': coupon_code,
            }

            return JsonResponse(response)

        except Exception as e:
            msg = 'An error occurred while processing the coupon.'
            response = {
                'msg': msg,
            }
            return JsonResponse(response)
