from datetime import date
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from django.shortcuts import get_object_or_404, render
from .models import Deal, Category, Merchant, Coupon

TODAY = date.today()

def _discount_expr():
    return ExpressionWrapper(
        (F("price_original") - F("price_discount")) * 100.0 / F("price_original"),
        output_field=FloatField()
    )

def home(request):
    top_deals = (
        Deal.objects
        .filter(starts_at__lte=TODAY, expires_at__gte=TODAY)
        .annotate(discount_pct=_discount_expr())
        .order_by("-discount_pct", "price_discount")[:8]
    )

    ending_soon = (
        Deal.objects
        .filter(expires_at__gte=TODAY)
        .annotate(discount_pct=_discount_expr())
        .order_by("expires_at")[:8]
    )

    cat_stats = (
        Category.objects
        .annotate(active_count=Count(
            "deal",
            filter=Q(deal__starts_at__lte=TODAY, deal__expires_at__gte=TODAY)
        ))
        .order_by("-active_count", "name")[:10]
    )

    kpi = Deal.objects.filter(starts_at__lte=TODAY, expires_at__gte=TODAY)\
        .annotate(discount_pct=_discount_expr())\
        .aggregate(
            total_active=Count("id"),
            max_discount_pct=Count("id") * 0 + ( )
        )

    ctx = dict(top_deals=top_deals, ending_soon=ending_soon, cat_stats=cat_stats, kpi=kpi)
    return render(request, "discounts/home.html", ctx)

def deal_detail(request, pk: int):
    deal = get_object_or_404(
        Deal.objects.annotate(discount_pct=_discount_expr()),
        pk=pk
    )
    coupons = Coupon.objects.filter(deal_id=deal.id).order_by("-issued_at")[:5]
    return render(request, "discounts/deal_detail.html", {"deal": deal, "coupons": coupons, "today": TODAY})

def category_page(request, cat_id: int):
    cat = get_object_or_404(Category, id=cat_id)
    deals = (
        Deal.objects.filter(category=cat, starts_at__lte=TODAY, expires_at__gte=TODAY)
        .annotate(discount_pct=_discount_expr())
        .exclude(discount_pct__lt=5)
        .order_by("-discount_pct", "price_discount")
    )
    return render(request, "discounts/category.html", {"category": cat, "deals": deals})

def search(request):
    q = (request.GET.get("q") or "").strip()
    results = []
    if q:
        results = (
            Deal.objects
            .filter(
                Q(title__icontains=q) |
                Q(merchant__name__icontains=q)
            )
            .annotate(discount_pct=_discount_expr())
            .distinct()
            .order_by("-discount_pct", "title")
        )
    return render(request, "discounts/search.html", {"q": q, "results": results})