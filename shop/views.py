from django.shortcuts import render, get_object_or_404,redirect
from category.models import Categories, SubCategories
from .models import Products, Variation,Filter_Price
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from django.db.models import Q




def store(request,category_slug=None,subcategory_slug=None):
    categories = None
    subcategories = None
    products = None
    selected_size = request.GET.get('size')  #

    sort_option = request.GET.get('sort', 'x')


    if category_slug!=None:
        categories = get_object_or_404(Categories,is_listed=True,slug=category_slug)
        products = Products.objects.filter(category_name=categories,is_available=True)
        product_count=products.count()

    elif subcategory_slug!=None:
        subcategories=get_object_or_404(SubCategories,slug=subcategory_slug,is_available=True)
        products=Products.objects.filter(subcategory_name=subcategories,is_available=True)
        product_count=products.count()


    else:
        categories=Categories.objects.filter(is_listed=True)
        for c in categories:
         print(c.name)
        subcategories=SubCategories.objects.filter(is_available=True)
        products=Products.objects.all().filter(is_available=True).order_by('product_name')
        for c in products:
         print(c.product_name)
        product_count = products.count()

    if sort_option == 'name_desc':
        products = products.order_by('-product_name')
    elif sort_option == 'price_asc':
        products = products.order_by('price')
    elif sort_option == 'price_desc':
        products = products.order_by('-price')
    elif sort_option == 'date_asc':
        products = products.order_by('created_date')
    elif sort_option == 'date_desc':
        products = products.order_by('-created_date')
    else:
        products = products.order_by('product_name')

    if selected_size:
        products = products.filter(variation__variation_value=selected_size)

    paginator = Paginator(products, per_page=3)
    page_number = request.GET.get('page', 1)
    page_products = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'products': page_products,
        'product_count': product_count,
        'sort_option': sort_option,
        'selected_sizes': selected_size,

    }

    return render(request, 'shop/store.html',context)



@login_required(login_url = 'login')
@never_cache
def search(request):
    try:
        keyword = request.GET.get('keyword', '')  # Use get() to provide a default value of an empty string
        products = Products.objects.order_by('-created_date').filter(Q(product_name__icontains=keyword))
        product_count = products.count()

        paginator = Paginator(products, per_page=1)
        page_number = request.GET.get('page', 1)
        page_products = paginator.get_page(page_number)

        context = {
            'products': page_products,
            'product_count': product_count,
        }
        return render(request, 'shop/search_result.html', context)

    except Exception as e:
        error_message = "An error occurred while processing your search."
        context = {
            'error_message': error_message,
        }
        return render(request, 'includes/404.html', context)



@login_required(login_url = 'login')
@never_cache
def product_details(request, category_slug, subcategory_slug, product_slug):
    try:
        categories = Categories.objects.all()

        product = get_object_or_404(
            Products,
            category_name__slug=category_slug,
            subcategory_name__slug=subcategory_slug,
            slug=product_slug
        )

        related_products = Products.objects.filter(subcategory_name__slug=subcategory_slug)[:4]
        variation=Variation.objects.all()



        context = {
            'categories': categories,
            'prod': product,
            "related_products": related_products,
            'variation':variation,

        }

    except Products.DoesNotExist:
        # Handle the case where the product does not exist
        context = {'error_message': 'Product not found'}

    except Exception as e:
        # Handle other exceptions
        context = {'error_message': 'An error occurred'}

    return render(request, 'shop/productdetails.html', context)




def error_404(request,exception):
    return render(request,'includes/404.html')




