from django.core.management.base import BaseCommand
from django.utils.timezone import now
from discounts.models import Discount

class Command(BaseCommand):
    help = 'Автоматически деактивирует скидки, срок которых истёк'

    def handle(self, *args, **kwargs):
        today = now().date()
        expired = Discount.objects.filter(end_date__lt=today, is_active=True)
        count = expired.update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f'✅ Деактивировано {count} скидок'))