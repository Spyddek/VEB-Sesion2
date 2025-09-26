from django.db import models
from django.conf import settings


class Role(models.Model):
    name = models.CharField("Роль", max_length=50, unique=True)

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class Merchant(models.Model):
    name = models.CharField("Название партнёра", max_length=255)
    contact = models.EmailField("Контактный email", blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Категория", max_length=100, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Deal(models.Model):
    title = models.CharField("Название предложения", max_length=255)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, verbose_name="Партнёр")
    price_original = models.DecimalField("Цена без скидки", max_digits=10, decimal_places=2)
    price_discount = models.DecimalField("Цена со скидкой", max_digits=10, decimal_places=2)
    starts_at = models.DateTimeField("Дата начала", null=True, blank=True)
    expires_at = models.DateTimeField("Дата окончания", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    categories = models.ManyToManyField("Category", through="DealCategory", verbose_name="Категории")
    image_url = models.URLField("Картинка (URL)", blank=True, default="")

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"

    def __str__(self):
        return self.title

    def discount_percent(self):
        """Вычисляем процент скидки"""
        if self.price_original and self.price_original > 0:
            return round(100 - (self.price_discount / self.price_original * 100), 2)
        return 0
    discount_percent.short_description = "Скидка (%)"

    @property
    def discount_pct(self):
        """Алиас для шаблонов"""
        return self.discount_percent()


class DealCategory(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Категория предложения"
        verbose_name_plural = "Категории предложений"

    def __str__(self):
        return f"{self.deal} — {self.category}"


class Coupon(models.Model):
    STATUS_CHOICES = [
        ("active", "Активен"),
        ("redeemed", "Использован"),
        ("expired", "Истёк"),
    ]
    code = models.CharField("Код купона", max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, verbose_name="Предложение")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="active")
    issued_at = models.DateTimeField("Дата выдачи", auto_now_add=True)
    redeemed_at = models.DateTimeField("Дата использования", null=True, blank=True)

    class Meta:
        verbose_name = "Купон"
        verbose_name_plural = "Купоны"

    def __str__(self):
        return f"{self.code} ({self.status})"
