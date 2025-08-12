# app sale models
from django.db import models
from unit.models import ProductUnit
from django.utils.translation import gettext_lazy as _
from trading_day.models import Event


class Sale(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='sale')
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Продажа {self.product_unit.serial_number} — {self.price}"
