from django.db import models
import os
from django.utils.text import slugify
from  django.urls import reverse


# Create your models here.


class Categories(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(max_length=500, null=False, blank=False)
    category_offer = models.FloatField(blank=False, null=False,default=0)
    is_listed=models.BooleanField(default=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Categories, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('products_by_categories', args=[self.slug])


class SubCategories(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, null=False, blank=False)
    is_featured=models.BooleanField(default=False)
    is_available=models.BooleanField(default=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(SubCategories, self).save(*args, **kwargs)



    def get_url(self):
        return reverse('products_by_sub_categories', args=[self.category.slug, self.slug])



