from django.contrib import admin
from .models import Request, RequestItem
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

class RequestItemInline(admin.TabularInline):
    """Инлайн для позиций заявки"""
    model = RequestItem
    extra = 1
    fields = (
        'product',
        'quantity',
        'price_per_unit',
        'supplier',
        'customer',
        'total_cost_display'
    )
    readonly_fields = ('total_cost_display',)

    def total_cost_display(self, instance):
        return f"{instance.total_cost:.2f} ₽"

    total_cost_display.short_description = _('Общая стоимость')


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    """Админка заявок"""
    list_display = (
        'id',
        'created_at',
        'status_display',
        'notes_short',
        'items_count'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('notes', 'items__product__name')
    inlines = (RequestItemInline,)
    fields = ('status', 'notes', 'created_at')
    readonly_fields = ('created_at',)

    def status_display(self, obj):
        status_colors = {
            'candidate': 'orange',
            'in_request': 'blue',
            'extra': 'purple'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = _('Статус')

    def notes_short(self, obj):
        return obj.notes[:50] + '...' if obj.notes else ''

    notes_short.short_description = _('Примечания')

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = _('Товаров')


@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    """Админка позиций заявки"""
    list_display = (
        'product',
        'request_link',
        'quantity',
        'price_per_unit',
        'total_cost_display',
        'supplier',
        'customer'
    )
    list_filter = ('request__status',)
    search_fields = ('product__name', 'request__id')

    def request_link(self, obj):
        return format_html(
            '<a href="/admin/request/request/{}/change/">{}</a>',
            obj.request.id,
            obj.request
        )

    request_link.short_description = _('Заявка')

    def total_cost_display(self, obj):
        return f"{obj.total_cost:.2f} ₽"

    total_cost_display.short_description = _('Общая стоимость')