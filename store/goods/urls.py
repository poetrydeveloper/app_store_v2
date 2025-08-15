from django.urls import path
from . import views

app_name = 'goods'

urlpatterns = [
    # Каталог товаров
    path('products/', views.products_view, name='products_view'),

    # Детали товара
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Поиск товаров
    path('search/', views.search_products, name='search_products'),
]