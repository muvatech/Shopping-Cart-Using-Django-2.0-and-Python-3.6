from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm

CATEGORIES_CACHE_KEY = 'shop_categories'
CATEGORIES_CACHE_TTL = 60 * 60
PRODUCTS_PER_PAGE = 25


def product_list(request, category_slug=None):
    category = None

    categories = cache.get(CATEGORIES_CACHE_KEY)
    if categories is None:
        categories = list(Category.objects.all())
        cache.set(CATEGORIES_CACHE_KEY, categories, CATEGORIES_CACHE_TTL)

    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.select_related('category'), id=id, slug=slug, available=True
    )
    cart_product_form = CartAddProductForm()
    context = {
        'product': product,
        'cart_product_form': cart_product_form
    }
    return render(request, 'shop/product/detail.html', context)
