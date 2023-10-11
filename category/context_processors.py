# dd.py
from .models import Categories,SubCategories
from shop.models import   Variation



def categories_link(request):
    cat_links = Categories.objects.filter(is_listed=True)
    return {'cat_links': cat_links}

def subcategories_link(request):
    subcat_links = SubCategories.objects.filter(is_available=True)
    return {'subcat_links': subcat_links}

def variation_link(request):
    var_links = Variation.objects.all()
    return {'var_links': var_links}
