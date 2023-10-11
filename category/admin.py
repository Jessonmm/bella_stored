from django.contrib import admin
from .models import Categories, SubCategories

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug': ('name',)}
  list_display = ('name', 'slug')

admin.site.register(Categories,CategoryAdmin)


class SubcategoryAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug':('name',)}
  list_display = ('name', 'slug', 'is_featured')



admin.site.register(SubCategories,SubcategoryAdmin)