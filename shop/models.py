from django.db import models
import os
from django.utils.text import slugify
from  django.urls import reverse
from category.models import  *

class Products(models.Model):
    product_name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_name = models.ForeignKey(Categories, on_delete=models.CASCADE)
    subcategory_name = models.ForeignKey(SubCategories, on_delete=models.CASCADE)
    price = models.IntegerField(blank=False)
    stock = models.IntegerField()
    product_offer = models.FloatField(blank=False, null=False,default=0)
    image_1 = models.ImageField(upload_to='uploads', max_length=None)
    image_2 = models.ImageField(upload_to='uploads', max_length=None)
    image_3 = models.ImageField(upload_to='uploads', max_length=None)
    image_4 = models.ImageField(upload_to='uploads', max_length=None)
    image_5 = models.ImageField(upload_to='uploads', max_length=None)
    description = models.TextField(max_length=500, null=False, blank=False)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Products, self).save(*args, **kwargs)



    def discount_price(self):
        product_discount = int(self.price) * (int(self.product_offer)) / 100

        category_discount = int(self.price) * (int(self.category_name.category_offer)) / 100

        if int(product_discount) >= int(category_discount):
            return product_discount
        else:
            return category_discount

    def offer_price(self):
        product_discount = int(self.price) * (int(self.product_offer)) / 100
        product_offer=int(self.price)-int(product_discount)

        category_discount = int(self.price) * (int(self.category_name.category_offer)) / 100
        category_offer = int(self.price) - int(category_discount)

        if not self.category_name.category_offer:
            return int(category_offer)

        if not self.product_offer:
            return int(category_offer)

        if int(product_offer) >= int(category_offer):
            return category_offer
        else:
            return product_offer


    def offer(self):
        product_offer=int(self.product_offer)
        category_offer=int(self.category_name.category_offer)
        if product_offer>=category_offer:
            return product_offer
        else:
            return category_offer


    def get_url(self):
        return reverse('product_details', args=[self.category_name.slug, self.subcategory_name.slug, self.slug])


class Filter_Price(models.Model):
    Filter_Price=(
        ('50 TO 1000','50 TO 1000'),
        ('1000 TO 5000','1000 TO 5000'),
        ('5000 TO 10000','5000 TO 10000'),
        ('10000 TO 50000','10000 TO 50000'),
        ('50000 TO 100000','50000 TO 100000'),

    )
    products = models.ForeignKey(Products, on_delete=models.CASCADE)




class VariationManager(models.Manager):
    def sizes(self):
        return self.filter(variation_category='size', is_active=True)

    def colors(self):
        return self.filter(variation_category='color',is_active=True)


variation_category_choices=(
    ('size','size'),
    ('color','color'),
     )

class Variation(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choices)
    variation_value=models.CharField(max_length=100)
    price_multiplier = models.IntegerField(default=1)
    is_active=models.BooleanField(default=False)
    variation_price=models.IntegerField(default=0)
    created_date=models.DateTimeField(auto_now=True)

    objects=VariationManager()

    def __str__(self):
        return self.variation_value

