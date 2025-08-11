from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from goods.models import Product

class Request(models.Model):
    """Модель заявки"""
    class Status(models.TextChoices):
        CANDIDATE = 'candidate', _('Кандидат на заявку')
        IN_REQUEST = 'in_request', _('В заявке')
        EXTRA = 'extra', _('В заявке экстра')

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    status = models.CharField(_('Статус'), max_length=20, choices=Status.choices, default=Status.CANDIDATE)
    notes = models.TextField(_('Примечания'), blank=True)

    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} ({self.get_status_display()})"

class RequestItem(models.Model):
    """Позиция в заявке"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='items', verbose_name=_('Заявка'))
    delivered_quantity = models.PositiveIntegerField(_('Поставлено'), default=0, help_text=_('Количество уже поставленных единиц'))
    is_completed = models.BooleanField(_('Выполнено'), default=False, help_text=_('Заявка полностью выполнена'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='request_items', verbose_name=_('Товар'))
    quantity = models.PositiveIntegerField(_('Количество'), default=1)
    price_per_unit = models.DecimalField(_('Цена за единицу'), max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(_('Поставщик'), max_length=255, default='неизвестный поставщик')
    customer = models.CharField(_('Покупатель'), max_length=255, default='покупатель')

    def clean(self):
        super().clean()
        if not self._state.adding and self.price_per_unit <= 0:
            raise ValidationError({'price_per_unit': _('Цена должна быть больше 0.')})
        if self.quantity < 1:
            raise ValidationError({'quantity': _('Количество не может быть меньше 1.')})

    def save(self, *args, **kwargs):
        if not self.pk and self.price_per_unit is None:
            self.price_per_unit = 0
        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        return self.price_per_unit * self.quantity

    @property
    def delivery_progress(self):
        return f"{self.delivered_quantity}/{self.quantity}"

    @property
    def remaining_quantity(self):
        return max(0, self.quantity - self.delivered_quantity)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"