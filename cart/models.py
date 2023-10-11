from django.db import models
from shop.models import *
# from orders.models import Coupon
from accounts.models import Account



class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.cart_id)




class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    variations = models.ManyToManyField(Variation, blank=True)
    price = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    full_price = models.IntegerField(default=0)


    def sub_total(self):
        return round(int(self.price) * int(self.quantity))

    def __str__(self):
        return str(self.product)

    def __str__(self):
        variations_str = ", ".join(str(variation) for variation in self.variation.all())
        return f"{self.product.product_name} - {variations_str} - Quantity: {self.quantity}"

ca=CartItem()
