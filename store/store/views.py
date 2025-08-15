# app store views
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from goods.models import Product, Category


def home_view(request):
    return render(request, 'store/home.html')

def main_view(request):
    return render(request, 'store/main.html')


def goods_view(request):
    categories = Category.objects.prefetch_related('children')
    products = Product.objects.all()
    return render(request, 'store/goods.html', {
        'categories': categories,
        'products': products
    })

def search_products(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        products = Product.objects.filter(name__icontains=query)[:10]
        results = [{'id': p.id, 'name': p.name} for p in products]
    return JsonResponse({'results': results})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})