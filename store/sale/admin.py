# sale/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('event_link', 'product_unit_link', 'price')
    search_fields = ('product_unit__serial_number', 'event__description')
    list_filter = ('event__trading_day__date',)

    def event_link(self, obj):
        url = reverse('admin:trading_day_event_change', args=[obj.event_id])
        return format_html('<a href="{}">{}</a>', url, obj.event)
    event_link.short_description = "Событие"

    def product_unit_link(self, obj):
        url = reverse('admin:unit_productunit_change', args=[obj.product_unit_id])
        return format_html('<a href="{}">{}</a>', url, obj.product_unit.serial_number)
    product_unit_link.short_description = "Карточка товара"
