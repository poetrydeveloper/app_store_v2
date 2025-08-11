# trading_day/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import TradingDay, Event
from sale.models import Sale

class SaleInline(admin.StackedInline):
    model = Sale
    extra = 0
    readonly_fields = ('price', 'product_unit_link')

    def product_unit_link(self, obj):
        if obj.product_unit_id:
            url = reverse('admin:unit_productunit_change', args=[obj.product_unit_id])
            return format_html('<a href="{}">{}</a>', url, obj.product_unit.serial_number)
        return "-"
    product_unit_link.short_description = "Карточка товара"

class EventAdminInline(admin.TabularInline):
    model = Event
    extra = 0
    readonly_fields = ('type', 'created_at', 'description_short', 'show_sale')
    can_delete = False
    show_change_link = True  # Можно переходить в редактирование события

    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description
    description_short.short_description = "Описание"

    def show_sale(self, obj):
        try:
            sale = obj.sale  # OneToOneField на Sale
            url = reverse('admin:sale_sale_change', args=[sale.id])
            return format_html('<a href="{}">Продажа: {}</a>', url, sale.price)
        except Sale.DoesNotExist:
            return "-"
    show_sale.short_description = "Продажа"

@admin.register(TradingDay)
class TradingDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'events_count')
    date_hierarchy = 'date'
    search_fields = ('date',)

    inlines = [EventAdminInline]

    def events_count(self, obj):
        return obj.events.count()
    events_count.short_description = "Количество событий"



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('trading_day_link', 'type', 'created_at', 'description_short')
    list_filter = ('type', 'trading_day__date')
    search_fields = ('description',)
    date_hierarchy = 'created_at'

    def trading_day_link(self, obj):
        url = reverse('admin:trading_day_tradingday_change', args=[obj.trading_day_id])
        return format_html('<a href="{}">{}</a>', url, obj.trading_day.date)
    trading_day_link.short_description = "Торговый день"

    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description
    description_short.short_description = "Описание"