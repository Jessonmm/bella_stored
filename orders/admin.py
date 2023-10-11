from django.contrib import admin
from .models import *

# Register your models here.

class OrderProductInline(admin.TabularInline):
  model = OrderProduct
  extra = 0

class PaymentAdmin(admin.ModelAdmin):
  list_display = ['user', 'order_id','payment_method', 'amount_paid', 'payment_id', 'status','created_at']
  list_per_page =  20
  inlines = [OrderProductInline]
class OrderProductAdmin(admin.ModelAdmin):
  list_display = ['order', 'payment','user', 'product', 'get_variations', 'quantity','product_price','ordered','created_at','updated_at']

  def get_variations(self,obj):
    return obj.variations
  get_variations.short_description='Variations'
class OrderAdmin(admin.ModelAdmin):
  list_display = ['order_number', 'full_name', 'phone_number','created_at', 'email', 'order_total', 'status', 'is_ordered']
  list_per_page =  20
  inlines = [OrderProductInline]

admin.site.register(Payment,PaymentAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct,OrderProductAdmin)
admin.site.register(Address)
admin.site.register(Coupons)
admin.site.register(UserCoupon)
admin.site.register(Wallet)
