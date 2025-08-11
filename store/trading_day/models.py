# trading_day/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class TradingDay(models.Model):
    date = models.DateField(_('Дата торгового дня'), default=timezone.now, unique=True)

    def __str__(self):
        return f"Торговый день {self.date}"


class Event(models.Model):
    class EventType(models.TextChoices):
        SALE = 'sale', _('Продажа')
        RETURN = 'return', _('Возврат')
        OTHER = 'other', _('Другое')

    trading_day = models.ForeignKey(
        TradingDay,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('Торговый день')
    )
    type = models.CharField(_('Тип события'), max_length=20, choices=EventType.choices)
    created_at = models.DateTimeField(_('Время события'), default=timezone.now)
    description = models.TextField(_('Описание'), blank=True)

    def __str__(self):
        return f"{self.get_type_display()} — {self.created_at:%H:%M}"