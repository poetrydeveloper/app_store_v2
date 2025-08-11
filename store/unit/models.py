import uuid
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

class ProductUnit(models.Model):
    """Единица товара, полученная из поставки"""

    serial_number = models.CharField(
        _('Серийный номер'),
        max_length=50,
        unique=True,
        editable=False
    )
    product = models.ForeignKey(
        'goods.Product',  # указываем через app_label.model_name
        on_delete=models.PROTECT,
        verbose_name=_('Товар')
    )
    delivery = models.ForeignKey(
        'delivery.Delivery',  # указываем через app_label.model_name
        on_delete=models.CASCADE,
        related_name='product_units',
        verbose_name=_('Поставка')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Единица товара')
        verbose_name_plural = _('Единицы товара')

    @classmethod
    def generate_serial_number(cls, product):
        """Генерация уникального серийного номера: RF-{product_id}-{timestamp}-{random_part}"""
        if not product or not product.pk:
            raise ValidationError("Товар должен быть сохранён перед генерацией номера.")

        base_prefix = f"RF-{product.id}-"
        timestamp = datetime.now().strftime("%d%m%H%M%S")  # день, месяц, часы, минуты, секунды
        random_part = f"{datetime.now().microsecond:06d}"  # микросекунды
        serial_number = f"{base_prefix}{timestamp}-{random_part}"

        if cls.objects.filter(serial_number=serial_number).exists():
            raise ValidationError("Не удалось сгенерировать уникальный серийный номер. Попробуйте снова.")

        return serial_number

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = self.generate_serial_number(self.product)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.serial_number})"
