from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from discounts.models import Role, Merchant, Category, Deal, DealCategory
from decimal import Decimal
import random


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        def get_image_url(i):
            return f"https://picsum.photos/seed/deal{i}/600/400"

        # роли можно оставить, если используешь где-то ещё
        roles = [Role.objects.get_or_create(name=n)[0] for n in ["user", "partner", "admin"]]

        # создаём пользователей
        users = []
        for i in range(1, 21):
            u, created = User.objects.get_or_create(
                username=f"user{i}",
                defaults={"email": f"user{i}@example.com"}
            )
            if created:
                u.set_password("test12345")  # пароль по умолчанию
                u.save()
            users.append(u)

        # создаём партнёров
        partners = []
        for i in range(1, 21):
            p, _ = Merchant.objects.get_or_create(
                name=f"Partner {i}",
                defaults={
                    "contact": f"partner{i}@example.com",
                    "user": random.choice(users),
                }
            )
            partners.append(p)

        # категории
        category_names = [
            "Электроника", "Одежда", "Обувь", "Продукты", "Красота и здоровье",
            "Дом и сад", "Спорт", "Игрушки", "Авто", "Книги"
        ]
        cats = [Category.objects.get_or_create(name=name)[0] for name in category_names]

        # возможные названия сделок по категориям
        deal_titles = {
            "Электроника": ["Скидка на смартфоны", "Уценка телевизоров", "Ноутбуки по акции"],
            "Одежда": ["Распродажа футболок", "Скидки на куртки", "Платья по суперцене"],
            "Обувь": ["Кроссовки со скидкой", "Сапоги по акции", "Туфли по спеццене"],
            "Продукты": ["Скидка на кофе", "Сыры по акции", "Фрукты по выгодной цене"],
            "Красота и здоровье": ["Скидки на косметику", "Парфюм по акции", "Витамины по суперцене"],
            "Дом и сад": ["Мебель со скидкой", "Акция на посуду", "Садовые товары по суперцене"],
            "Спорт": ["Скидка на велосипеды", "Тренажёры по акции", "Спортивная одежда со скидкой"],
            "Игрушки": ["Конструкторы по суперцене", "Куклы со скидкой", "Настольные игры по акции"],
            "Авто": ["Автоаксессуары со скидкой", "Шины по акции", "Масла и жидкости по суперцене"],
            "Книги": ["Бестселлеры по акции", "Учебники со скидкой", "Фэнтези по суперцене"],
        }

        # создаём минимум 30 сделок
        deals = []
        now = timezone.now()
        for i in range(1, 31):
            orig = Decimal(random.randint(500, 5000))
            disc = orig * Decimal(random.choice([0.5, 0.6, 0.7]))
            image_url = get_image_url(i)

            cat = random.choice(cats)
            title = random.choice(deal_titles.get(cat.name, [f"Специальное предложение {i}"]))

            d, _ = Deal.objects.get_or_create(
                title=title,
                merchant=random.choice(partners),
                defaults={
                    "price_original": orig,
                    "price_discount": disc,
                    "starts_at": now,
                    "expires_at": now + timezone.timedelta(days=random.randint(5, 45)),
                    "image_url": image_url
                }
            )
            # основная категория + ещё одна
            DealCategory.objects.get_or_create(deal=d, category=cat)
            for c in random.sample(cats, k=1):
                DealCategory.objects.get_or_create(deal=d, category=c)

            deals.append(d)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ База успешно наполнена: {len(deals)} акций, {len(users)} пользователей, {len(partners)} партнёров"
            )
        )
