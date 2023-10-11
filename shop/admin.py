from django.contrib import admin
from .models import *

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
  list_display = ('product_name', 'price', 'category_name', 'subcategory_name', 'modified_date', 'is_featured', 'is_available','image_1','image_2','image_3','image_4','image_5')
  prepopulated_fields = {'slug':('product_name',)}

class VariationAdmin(admin.ModelAdmin):
  list_display=('product','variation_category','variation_value','is_active')
  list_editable=('is_active',)
  list_filter=('product','variation_category','variation_value')



admin.site.register(Products,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
