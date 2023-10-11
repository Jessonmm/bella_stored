from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import never_cache
from  django.http import HttpResponseRedirect
from shop.models import Products, Variation
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from orders.models import Address
from django.db.models import Q
from orders.models import *



def _cart_id(request):
  cart = request.session.session_key
  if not cart:
    cart = request.session.create()
  return cart

@login_required(login_url = 'login')
@never_cache
def cart(request, total=0, quantity=0, cart_items=None):
    if not request.user.is_authenticated:
        return redirect('login')
    tax = 0
    grand_total = 0
    product_price = 0
    shipping=0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')

        for cart_item in cart_items:

            variations = cart_item.variations.all().values_list('price_multiplier')

            if variations:
                price_mult = int(variations[0][0])
            else:
                price_mult = 1


            product_price = int(cart_item.product.offer_price()) * price_mult
            total += int(product_price )* int(cart_item.quantity)
            quantity += cart_item.quantity
            cart_item.price = int(product_price)
            cart_item.save()

        tax = round(int((5 * total) / 100))
        shipping = round(int((2 * total) / 100))

        if shipping <= 18:
            shipping = 0
        elif shipping > 18 and shipping <= 35:
            shipping = 35
        else:
            shipping = round(int((2 * total) / 100))
        grand_total = int(tax + total + shipping)

        for c in cart_items:
            c.full_prices=grand_total
            print(c.full_prices)
            c.save()
        print(grand_total)


    except ObjectDoesNotExist:
        messages.error(request, 'An error occurred while processing your cart.')
        return redirect('store')

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping':shipping,
        'grand_total': grand_total,
    }
    return render(request, 'cart/cart.html', context)


@login_required(login_url = 'login')
@never_cache
def add_cart(request, product_id):
    current_user = request.user
    product = Products.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')

    # if user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))

        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')

@login_required(login_url = 'login')
@never_cache
def cart_remove(request, product_id, cart_item_id):
    try:
        product = get_object_or_404(Products, id=product_id)

        if request.user.is_authenticated:
            cartitem = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = get_object_or_404(Cart, cart_id=_cart_id(request))
            cartitem = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cartitem.quantity > 1:
            cartitem.quantity -= 1
            cartitem.save()
            messages.success(request,'item quantity reduced successfully')
        else:
            cartitem.delete()

    except CartItem.DoesNotExist:
        messages.error(request, 'The selected item could not be found in your cart.')
    except Exception as e:
        messages.error(request, 'An error occurred while removing the item from your cart.')

    return redirect('cart')

@login_required(login_url = 'login')
@never_cache
def cart_update(request, product_id, cart_item_id):
    try:
        product = get_object_or_404(Products, id=product_id)

        if request.user.is_authenticated:
            cartitem = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cartitem = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        cartitem.quantity += 1
        cartitem.save()
        messages.success(request,'item quantity added successfully')

    except CartItem.DoesNotExist:
        messages.error(request, 'The selected item could not be found in your cart.')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart could not be found.')

    return redirect('cart')

@login_required(login_url = 'login')
@never_cache
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Products, id=product_id)

    try:
        if request.user.is_authenticated:
            cartitem = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cartitem = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        cartitem.delete()
        messages.success(request, 'Item removed from your cart.')

    except CartItem.DoesNotExist:
        messages.error(request, 'The selected item could not be found in your cart.')

    return redirect('cart')





@login_required(login_url = 'login')
@never_cache
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        total = 0
        quantity = 0
        tax = 0
        shipping = 0
        grand_total = 0
        address = Address.objects.filter(user=request.user)
        cart_items = None

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += int(cart_item.price) * int(cart_item.quantity)
            quantity += cart_item.quantity

        tax = round(int((5 * total) / 100))
        shipping = round(int((2 * total) / 100))

        if shipping <= 18:
            shipping = 0
        elif shipping > 18 and shipping <= 35:
            shipping = 35
        else:
            shipping = round(int((2 * total) / 100))

        grand_total = int(tax + total + shipping)
        grand_total = format(grand_total, '.2f')

    except ObjectDoesNotExist:

        messages.error(request, 'An error occurred while processing your order.')
        return redirect('cart')

    coupons = Coupons.objects.filter(active=True)

    for item in coupons:
        try:
            coupon = UserCoupon.objects.get(user=request.user, coupon=item)
        except UserCoupon.DoesNotExist:
            coupon = UserCoupon()
            coupon.user = request.user
            coupon.coupon = item
            coupon.save()

    coupons = UserCoupon.objects.filter(user=request.user, used=False)

    context = {
        'address': address,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'coupons': coupons,
        'shipping': shipping,
    }
    print(grand_total)

    return render(request, 'cart/checkout.html', context)





