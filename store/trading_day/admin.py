from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from .models import TradingDay, Event
from sale.models import Sale

# Inline продажи внутри события — т.к. OneToOne, max_num=1, can_delete=False
class SaleInline(admin.StackedInline):
    model = Sale
    max_num = 1
    fk_name = 'event'
    fields = ('product_unit', 'price')
    autocomplete_fields = ('product_unit',)

    def product_unit_link(self, obj):
        if obj.product_unit_id:
            url = reverse('admin:unit_productunit_change', args=[obj.product_unit_id])
            return format_html('<a href="{}">{}</a>', url, obj.product_unit.serial_number)
        return "-"
    product_unit_link.short_description = "Карточка товара"

# Inline событий внутри торгового дня
class EventAdminInline(admin.TabularInline):
    model = Event
    extra = 0
    readonly_fields = ('type', 'created_at', 'description_short', 'show_sale')
    can_delete = False
    show_change_link = True
    inlines = [SaleInline]  # НЕ поддерживается по умолчанию — поэтому вместо вложенного inline используем переопределение формы или другие подходы

    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + "..."
        return obj.description
    description_short.short_description = "Описание"

    def show_sale(self, obj):
        try:
            sale = obj.sale  # OneToOneField
            url = reverse('admin:sale_sale_change', args=[sale.id])
            return format_html('<a href="{}">Продажа: {}</a>', url, sale.price)
        except Sale.DoesNotExist:
            return "-"
    show_sale.short_description = "Продажа"

# Поскольку Django не поддерживает вложенные inline, мы уберем вложение SaleInline внутрь EventAdminInline.
# Вместо этого сделаем SaleInline в EventAdmin (отдельный класс).

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
    list_display = ('type', 'created_at', 'description_short')
    list_filter = ('type',)
    search_fields = ('description',)

    inlines = [SaleInline]

    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + "..."
        return obj.description
    description_short.short_description = "Описание"
