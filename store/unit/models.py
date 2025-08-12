import uuid
from datetime import datetime
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ProductUnit(models.Model):
    """Модель для хранения единиц товара из поставок"""
    serial_number = models.CharField(
        _('Серийный номер'),
        max_length=100,
        unique=True,
        editable=False,
        help_text=_("Автоматически генерируется при создании")
    )
    product = models.ForeignKey(
        'goods.Product',
        on_delete=models.PROTECT,
        verbose_name=_('Товар'),
        related_name='units'
    )
    delivery = models.ForeignKey(
        'delivery.Delivery',
        on_delete=models.CASCADE,
        related_name='product_units',
        verbose_name=_('Поставка')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Единица товара')
        verbose_name_plural = _('Единицы товара')
        ordering = ['-created_at']

    @classmethod
    def generate_serial_number(cls, product, delivery):
        """
        Генерация уникального серийного номера в формате:
        {product_code}_{delivery_price}-{timestamp}-{random_uuid}
        """
        # Проверка наличия объектов
        if not product:
            print(f"ОШИБКА ГЕНЕРАЦИИ: Не указан товар")
            raise ValidationError("Не указан товар")

        if not delivery:
            print(f"ОШИБКА ГЕНЕРАЦИИ: Не указана поставка")
            raise ValidationError("Не указана поставка")

        # Проверка сохранности объектов в БД
        if not product.pk:
            print(f"ОШИБКА: Товар не сохранен! ID: {product.id if hasattr(product, 'id') else 'None'}")
            raise ValidationError("Товар должен быть сохранён в БД перед генерацией номера")

        if not delivery.pk:
            print(f"ОШИБКА: Поставка не сохранена! ID: {delivery.id if hasattr(delivery, 'id') else 'None'}")
            raise ValidationError("Поставка должна быть сохранена в БД перед генерацией номера")

        try:
            # Получаем необходимые данные
            product_code = product.code
            delivery_price = delivery.price_per_unit

            # Форматируем данные
            base_prefix = f"{product_code}_{delivery_price}-"
            timestamp = datetime.now().strftime("%d%m%H%M%S")  # ДеньМесяцЧасыМинутыСекунды
            unique_part = uuid.uuid4().hex[:8]  # Уникальная часть из UUID

            # Собираем полный номер
            serial_number = f"{base_prefix}{timestamp}-{unique_part}"

            print(f"Сгенерирован серийник: {serial_number}")
            return serial_number

        except AttributeError as e:
            print(f"ОШИБКА АТРИБУТА: {e}")
            raise ValidationError(f"Ошибка генерации серийного номера: {e}")
        except Exception as e:
            print(f"НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
            raise ValidationError("Системная ошибка генерации номера")

    def clean(self):
        """Валидация перед сохранением"""
        super().clean()

        # Проверяем наличие обязательных полей
        if not self.product_id:
            raise ValidationError({"product": "Товар обязателен"})

        if not self.delivery_id:
            raise ValidationError({"delivery": "Поставка обязательна"})

    def save(self, *args, **kwargs):
        """Переопределение сохранения с генерацией серийника"""
        print(f"Сохранение ProductUnit (ID: {self.id or 'новый'})")

        # Генерируем серийный номер если он отсутствует
        if not self.serial_number:
            print("Генерация серийного номера...")

            # Проверяем наличие связанных объектов
            if not hasattr(self, 'product'):
                print("КРИТИЧЕСКАЯ ОШИБКА: Отсутствует продукт!")
                raise ValidationError("Не указан товар")

            if not hasattr(self, 'delivery'):
                print("КРИТИЧЕСКАЯ ОШИБКА: Отсутствует поставка!")
                raise ValidationError("Не указана поставка")

            self.serial_number = self.generate_serial_number(
                self.product,
                self.delivery
            )
            print(f"Присвоен серийник: {self.serial_number}")

        # Сохраняем с обработкой конфликтов уникальности
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                super().save(*args, **kwargs)
                print(f"Успешное сохранение (попытка {attempt})")
                return  # Выходим при успешном сохранении

            except IntegrityError as e:
                if 'serial_number' in str(e).lower() and attempt < max_attempts:
                    # Перегенерируем номер при конфликте
                    print(f"КОНФЛИКТ СЕРИЙНИКА! Попытка {attempt}/{max_attempts}")
                    self.serial_number = self.generate_serial_number(
                        self.product,
                        self.delivery
                    )
                else:
                    print(f"КРИТИЧЕСКАЯ ОШИБКА СОХРАНЕНИЯ: {e}")
                    raise ValidationError(
                        f"Ошибка сохранения после {max_attempts} попыток: {e}"
                    )

    def __str__(self):
        """Строковое представление объекта"""
        return f"{self.product.name if hasattr(self, 'product') else 'No product'} [{self.serial_number}]"