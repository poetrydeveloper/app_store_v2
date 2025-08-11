# delivery/admin.py

from unit.models import ProductUnit  # Импортируем модель карточки товара

# delivery/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.apps import apps
from django.db import transaction

from .models import Delivery
from request.models import RequestItem, Request


class DeliveryCreationForm(forms.ModelForm):
    """Кастомная форма для создания поставки"""
    class Meta:
        model = Delivery
        fields = ['request_item', 'delivery_date', 'quantity', 'extra_shipment', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_date'].initial = timezone.now().date()


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    form = DeliveryCreationForm
    list_display = (
        'id', 'delivery_date', 'request_info', 'product_info',
        'quantity_display', 'status_display', 'extra_info', 'units_created'
    )
    list_filter = ('status', 'extra_shipment', 'delivery_date')
    search_fields = ('product__code', 'product__name', 'request_item__request__id')
    readonly_fields = (
        'status_display', 'request_info', 'product_info',
        'supplier_display', 'customer_display', 'price_display',
        'request_date_display', 'extra_request_display'
    )

    actions = ['generate_product_units']  # Новое действие

    fieldsets = (
        ('Основная информация', {
            'fields': ('request_item', 'delivery_date', 'quantity', 'extra_shipment', 'notes')
        }),
        ('Информация из заявки', {
            'fields': (
                'request_info', 'product_info', 'supplier_display', 'customer_display',
                'price_display', 'request_date_display', 'extra_request_display', 'status_display'
            ),
            'classes': ('collapse',)
        }),
    )

    # ==== Новое: отображение факта генерации карточек ====
    def units_created(self, obj):
        count = obj.product_units.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">Да ({})</span>', count)
        return format_html('<span style="color: red; font-weight: bold;">Нет</span>')
    units_created.short_description = "Карточки созданы"

    # ==== Новое: админское действие ====
    @transaction.atomic
    def generate_product_units(self, request, queryset):
        """Админ-действие: для выделенных поставок создать ProductUnit в количестве quantity.
           Если карточки уже существуют — пропустить поставку."""
        ProductUnit = apps.get_model('unit', 'ProductUnit')  # ленивый импорт, чтобы не было циклических импортов
        total_created = 0
        skipped = 0
        errors = []

        for delivery in queryset.select_for_update():
            # Проверяем, что есть связанный product
            if not getattr(delivery, 'product', None):
                errors.append(f"Поставка #{delivery.id}: нет связанного товара.")
                continue

            # Если карточки уже созданы — пропускаем
            if delivery.product_units.exists():
                skipped += 1
                continue

            # Генерируем записи в памяти (с уникальными serial_number)
            units = []
            try:
                for _ in range(delivery.quantity):
                    serial = ProductUnit.generate_serial_number(delivery.product)
                    units.append(ProductUnit(product=delivery.product, delivery=delivery, serial_number=serial))
            except Exception as e:
                errors.append(f"Поставка #{delivery.id}: ошибка генерации серийников: {e}")
                continue

            # Сохраняем пакетно
            ProductUnit.objects.bulk_create(units)
            total_created += len(units)

        # Сообщения в админке
        if total_created:
            self.message_user(request, f"Создано {total_created} карточек товара.", level=messages.SUCCESS)
        if skipped:
            self.message_user(request, f"Пропущено {skipped} поставок — карточки уже существуют.",
                              level=messages.WARNING)
        for e in errors:
            self.message_user(request, e, level=messages.ERROR)

    generate_product_units.short_description = "Сгенерировать карточки товара"

    # ==== Остальной код из твоей версии ====
    def request_info(self, obj):
        if obj.request_item_id:
            return format_html(
                '<a href="{}">Заявка #{}</a> (Статус: {})',
                reverse('admin:request_request_change', args=[obj.request_item.request_id]),
                obj.request_item.request_id,
                obj.request_item.request.get_status_display()
            )
        return '-'

    def product_info(self, obj):
        if obj.product_id:
            return format_html(
                '<a href="{}">{} ({})</a>',
                reverse('admin:goods_product_change', args=[obj.product_id]),
                obj.product.name,
                obj.product.code
            )
        return '-'

    def supplier_display(self, obj):
        return obj.supplier or '-'

    def customer_display(self, obj):
        return obj.customer or '-'

    def price_display(self, obj):
        return f"{obj.price_per_unit:.2f}" if obj.price_per_unit else '-'

    def request_date_display(self, obj):
        return obj.request_date or '-'

    def extra_request_display(self, obj):
        return _('Да') if obj.extra_request else _('Нет')

    def quantity_display(self, obj):
        if obj.request_item_id:
            requested = obj.request_item.quantity
            color = "green" if obj.quantity == requested else "orange"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} / {}</span>',
                color, obj.quantity, requested
            )
        return f"{obj.quantity}"

    def status_display(self, obj):
        if obj.status:
            colors = {'partial': 'orange', 'over': 'blue', 'full': 'green', 'extra': 'purple'}
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                colors.get(obj.status, 'black'), obj.get_status_display()
            )
        return _('Будет определен после сохранения')

    def extra_info(self, obj):
        if obj.extra_request or obj.extra_shipment:
            return format_html('Заявка: {}<br>Поставка: {}',
                               'Да' if obj.extra_request else 'Нет',
                               'Да' if obj.extra_shipment else 'Нет')
        return '-'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('request_item__request', 'product').prefetch_related('product_units')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "request_item":
            kwargs["queryset"] = RequestItem.objects.filter(
                request__status__in=[Request.Status.IN_REQUEST, Request.Status.EXTRA]
            ).exclude(delivered_quantity__gte=F('quantity')).select_related('product', 'request')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
