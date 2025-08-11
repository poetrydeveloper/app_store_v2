# unit/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ProductUnit


@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'product_link',
        'delivery_link',
        'created_at',
    )
    list_filter = ('created_at', 'product__category')
    search_fields = ('serial_number', 'product__name', 'product__code', 'delivery__id')
    ordering = ('-created_at',)

    readonly_fields = ('serial_number', 'created_at', 'product_link', 'delivery_link')

    fieldsets = (
        ('Основная информация', {
            'fields': ('serial_number', 'product_link', 'delivery_link', 'created_at')
        }),
    )

    def product_link(self, obj):
        if obj.product_id:
            url = reverse('admin:goods_product_change', args=[obj.product_id])
            return format_html('<a href="{}">{} ({})</a>', url, obj.product.name, obj.product.code)
        return '-'
    product_link.short_description = "Товар"

    def delivery_link(self, obj):
        if obj.delivery_id:
            url = reverse('admin:delivery_delivery_change', args=[obj.delivery_id])
            return format_html('<a href="{}">Поставка #{}</a>', url, obj.delivery.id)
        return '-'
    delivery_link.short_description = "Поставка"
