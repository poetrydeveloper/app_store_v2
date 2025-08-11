#app delivery/models
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from request.models import Request, RequestItem
from goods.models import Product


class Delivery(models.Model):
    """Модель поставки товара"""

    class Status(models.TextChoices):
        PARTIAL = 'partial', _('Частично получено')
        OVER = 'over', _('Переполучено')
        FULL = 'full', _('Полностью получено')
        EXTRA = 'extra', _('Экстра')

    request_item = models.ForeignKey(
        RequestItem,
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name=_('Позиция заявки')
    )
    delivery_date = models.DateField(_('Дата поставки'), default=timezone.now)
    quantity = models.PositiveIntegerField(_('Количество'), default=1)
    status = models.CharField(_('Статус'), max_length=20, choices=Status.choices, editable=False)
    extra_shipment = models.BooleanField(_('Экстра поставка'), default=False)
    notes = models.TextField(_('Примечания'), blank=True)

    # Автозаполняемые поля
    supplier = models.CharField(_('Поставщик'), max_length=255, editable=False)
    customer = models.CharField(_('Покупатель'), max_length=255, editable=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_('Товар'), editable=False)
    request_date = models.DateField(_('Дата заявки'), editable=False)
    extra_request = models.BooleanField(_('Экстра заявка'), editable=False)
    price_per_unit = models.DecimalField(_('Цена за единицу'), max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = _('Поставка')
        verbose_name_plural = _('Поставки')
        ordering = ['-delivery_date']

    def __str__(self):
        return f"Поставка #{self.id} - {self.product.name if self.product_id else '?'}"

    def clean(self):
        if not self.request_item_id:
            raise ValidationError(_('Необходимо выбрать позицию заявки'))

        request_item = self.request_item

        if self.delivery_date <= request_item.request.created_at.date():
            raise ValidationError({'delivery_date': _('Дата поставки должна быть позже даты заявки')})

        if self.quantity < 1:
            raise ValidationError({'quantity': _('Количество не может быть меньше 1')})

        if self.extra_shipment and request_item.request.status != Request.Status.EXTRA:
            raise ValidationError({'extra_shipment': _('Экстра поставка возможна только для экстра заявок')})

        # Проверка остатка
        remaining = request_item.quantity - request_item.delivered_quantity
        # Если редактируем существующую поставку — учитываем старое количество
        if self.pk:
            old_quantity = Delivery.objects.get(pk=self.pk).quantity
            remaining += old_quantity
        if self.quantity > remaining:
            raise ValidationError({'quantity': _('Максимально можно поставить {} единиц').format(remaining)})
        if remaining <= 0:
            raise ValidationError({'request_item': _('Заявка по этой позиции уже выполнена')})

    def save(self, *args, **kwargs):
        request_item = self.request_item

        # Заполняем поля из заявки
        self.supplier = request_item.supplier
        self.customer = request_item.customer
        self.product = request_item.product
        self.request_date = request_item.request.created_at.date()
        self.extra_request = (request_item.request.status == Request.Status.EXTRA)
        self.price_per_unit = request_item.price_per_unit

        # Определяем статус
        if self.extra_shipment:
            self.status = Delivery.Status.EXTRA
            if not self.notes:
                self.notes = (f"Экстра поставка на основании заявки {request_item.request.id} "
                              f"от {self.request_date}")
        else:
            requested_quantity = request_item.quantity
            if self.quantity < requested_quantity:
                self.status = Delivery.Status.PARTIAL
            elif self.quantity > requested_quantity:
                self.status = Delivery.Status.OVER
            else:
                self.status = Delivery.Status.FULL

        # Если редактируем — пересчитать delivered_quantity
        if self.pk:
            old_quantity = Delivery.objects.get(pk=self.pk).quantity
            request_item.delivered_quantity += self.quantity - old_quantity
        else:
            request_item.delivered_quantity += self.quantity

        # Обновляем флаг выполнения
        request_item.is_completed = request_item.delivered_quantity >= request_item.quantity
        request_item.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        request_item = self.request_item
        request_item.delivered_quantity -= self.quantity
        if request_item.delivered_quantity < request_item.quantity:
            request_item.is_completed = False
        request_item.save()
        super().delete(*args, **kwargs)
