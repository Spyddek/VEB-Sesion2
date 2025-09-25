from django.core.management.base import BaseCommand
from django.utils import timezone
from discounts.models import Role, User, Merchant, Category, Deal, DealCategory
from decimal import Decimal
import random


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        images = [f"images/deals/deal{i}.jpg" for i in range(1, 100)]

        roles = [Role.objects.get_or_create(name=n)[0] for n in ["user", "partner", "admin"]]

        users = []
        for i in range(1, 11):
            u, _ = User.objects.get_or_create(
                email=f"user{i}@example.com",
                defaults={"password_hash": f"hash{i}", "role": roles[0]}
            )
            users.append(u)

        partners = []
        for i in range(1, 11):
            p, _ = Merchant.objects.get_or_create(
                name=f"Partner {i}",
                defaults={"contact": f"partner{i}@example.com", "user": random.choice(users)}
            )
            partners.append(p)

        cats = []
        for i in range(1, 11):
            c, _ = Category.objects.get_or_create(name=f"Категория {i}")
            cats.append(c)

        deals = []
        now = timezone.now()
        for i in range(1, 11):
            orig = Decimal(random.randint(500, 5000))
            disc = orig * Decimal(random.choice([0.5, 0.6, 0.7]))
            image_url = images[(i - 1) % len(images)]
            d, _ = Deal.objects.get_or_create(
                title=f"Супер предложение {i}",
                merchant=random.choice(partners),
                defaults={
                    "price_original": orig,
                    "price_discount": disc,
                    "starts_at": now,
                    "expires_at": now + timezone.timedelta(days=random.randint(5, 45)),
                    "image_url": image_url
                }
            )
            for c in random.sample(cats, k=2):
                DealCategory.objects.get_or_create(deal=d, category=c)
            deals.append(d)

        self.stdout.write(self.style.SUCCESS("✅ База успешно наполнена тестовыми данными (локальные картинки)"))
