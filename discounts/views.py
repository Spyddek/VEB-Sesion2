from django.db.models import Count, Q, F, ExpressionWrapper, DecimalField
from django.shortcuts import render
from .models import Deal, Category

def home(request):
    # Виджет 1: Топ-скидки дня (аннотация % скидки)
    discount_expr = ExpressionWrapper(
        100 - (F("price_discount") * 100.0 / F("price_original")),
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
    top_deals = Deal.objects.annotate(discount_percent=discount_expr).order_by("-discount_percent")[:5]

    # Виджет 2: Скоро заканчиваются
    ending_soon = Deal.objects.filter(expires_at__isnull=False).order_by("expires_at")[:5]

    # Виджет 3: Популярные категории (агрегация)
    popular_categories = Category.objects.annotate(
        active_deals=Count("dealcategory__deal", distinct=True)
    ).order_by("-active_deals")[:5]

    return render(request, "home.html", {
        "top_deals": top_deals,
        "ending_soon": ending_soon,
        "popular_categories": popular_categories,
    })

def search(request):
    q = request.GET.get("q", "").strip()
    results = Deal.objects.none()
    if q:
        results = Deal.objects.filter(
            Q(title__icontains=q) |
            Q(merchant__name__icontains=q) |
            Q(categories__name__icontains=q)
        ).distinct().order_by("-created_at")
    return render(request, "search.html", {"q": q, "results": results})
