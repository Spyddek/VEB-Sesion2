from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


# -------------------------------
# 🔹 Роли пользователей
# -------------------------------
class Role(models.Model):
    name = models.CharField("Роль", max_length=50, unique=True)

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


# -------------------------------
# 🔹 Партнёры (магазины)
# -------------------------------
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


# -------------------------------
# 🔹 Категории
# -------------------------------
class Category(models.Model):
    name = models.CharField("Категория", max_length=100, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


# -------------------------------
# 🔹 Акции / Предложения
# -------------------------------
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
    description = models.TextField("Описание продукта", blank=True, null=True)

    # ✅ Добавлено поле для избранного
    favorited_by = models.ManyToManyField(
        User,
        related_name="favorite_deals",
        blank=True,
        verbose_name="Добавили в избранное"
    )

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"

    def __str__(self):
        return self.title

    # ✅ Автоматический расчёт и округление скидки
    def discount_percent(self):
        """Возвращает целый процент скидки"""
        if self.price_original and self.price_original > 0:
            discount = 100 - (self.price_discount / self.price_original * 100)
            return int(round(discount))  # округляем до целого
        return 0

    @property
    def discount_pct(self):
        return self.discount_percent()

# -------------------------------
# 🔹 Категории предложений (связка)
# -------------------------------
class DealCategory(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Категория предложения"
        verbose_name_plural = "Категории предложений"

    def __str__(self):
        return f"{self.deal} — {self.category}"


# -------------------------------
# 🔹 Купоны
# -------------------------------
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