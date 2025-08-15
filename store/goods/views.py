# app goods views

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from goods.models import Product, Category



def products_view(request):
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