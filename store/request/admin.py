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
        'delivered_quantity',
        'delivery_progress',
        'is_completed',
        'price_per_unit',
        'supplier',
        'customer',
        'total_cost_display'
    )
    readonly_fields = ('delivery_progress', 'total_cost_display')

    def delivery_progress(self, obj):
        """Отображает прогресс поставки с цветовой индикацией"""
        if obj.is_completed:
            color = "green"
            text = f"{obj.quantity}/{obj.quantity} ✓"
        elif obj.delivered_quantity > 0:
            color = "orange"
            text = f"{obj.delivered_quantity}/{obj.quantity}"
        else:
            color = "gray"
            text = f"0/{obj.quantity}"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )

    delivery_progress.short_description = _('Поставлено')

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
        'completion_status',
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

    def completion_status(self, obj):
        """Отображает статус выполнения всей заявки"""
        # Считаем прогресс по всем позициям
        total_items = obj.items.count()
        completed_items = obj.items.filter(is_completed=True).count()

        # Если нет позиций
        if total_items == 0:
            return format_html('<span style="color: gray;">Нет позиций</span>')

        # Если все позиции выполнены
        if completed_items == total_items:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Выполнена</span>'
            )

        return format_html(
            '<span style="color: orange;">{}/{} позиций</span>',
            completed_items,
            total_items
        )

    completion_status.short_description = _('Выполнение')

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
        'quantity_display',
        'delivery_progress',
        'is_completed',
        'price_per_unit',
        'total_cost_display',
        'supplier',
        'customer'
    )
    list_filter = ('request__status', 'is_completed')
    search_fields = ('product__name', 'request__id')
    list_editable = ('is_completed',)

    def request_link(self, obj):
        return format_html(
            '<a href="/admin/request/request/{}/change/">{}</a>',
            obj.request.id,
            obj.request
        )

    request_link.short_description = _('Заявка')

    def quantity_display(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            obj.quantity
        )

    quantity_display.short_description = _('Заказано')

    def delivery_progress(self, obj):
        """Отображает прогресс поставки с цветовой индикацией"""
        if obj.is_completed:
            color = "green"
            text = f"{obj.quantity}/{obj.quantity} ✓"
        elif obj.delivered_quantity > 0:
            color = "orange"
            text = f"{obj.delivered_quantity}/{obj.quantity}"
        else:
            color = "gray"
            text = f"0/{obj.quantity}"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )

    delivery_progress.short_description = _('Поставлено')

    def total_cost_display(self, obj):
        return f"{obj.total_cost:.2f} ₽"

    total_cost_display.short_description = _('Общая стоимость')

    def save_model(self, request, obj, form, change):
        """Принудительная проверка выполнения при ручном изменении флага"""
        if 'is_completed' in form.changed_data:
            if obj.is_completed:
                obj.delivered_quantity = obj.quantity
            else:
                obj.delivered_quantity = 0
        super().save_model(request, obj, form, change)