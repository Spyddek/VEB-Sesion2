from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import (
    Count,
    Q,
    Case,
    When,
    Value,
    IntegerField,
    F,
    ExpressionWrapper,
    FloatField,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal
from django.core.paginator import Paginator

from .models import Deal, Category, Merchant
from .forms import DealForm


def home(request):
    """Главная страница с блоками акций"""
    top_deals = sorted(
        Deal.objects.all(),
        key=lambda d: d.discount_percent(),
        reverse=True
    )[:8]

    ending_soon = Deal.objects.filter(
        expires_at__gt=timezone.now()
    ).order_by("expires_at")[:5]

    cat_stats = Category.objects.annotate(
        active_count=Count("dealcategory")
    ).order_by("-active_count")[:4]

    return render(request, "home.html", {
        "top_deals": top_deals,
        "ending_soon": ending_soon,
        "cat_stats": cat_stats,
    })


def search(request):
    """Продвинутый поиск по акциям, магазинам и категориям."""
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "relevance")
    raw_selected_categories = request.GET.getlist("category")

    # Преобразуем выбранные категории к списку целых чисел, игнорируя некорректные значения
    selected_categories = []
    for value in raw_selected_categories:
        try:
            selected_categories.append(int(value))
        except (TypeError, ValueError):
            continue

    selected_categories = list(dict.fromkeys(selected_categories))

    deals_page = None
    merchants = Merchant.objects.none()
    categories = Category.objects.none()
    deal_total = merchant_total = category_total = 0

    query_too_short = bool(q) and len(q) < 2
    show_results = bool(q) and not query_too_short

    category_queryset = Category.objects.annotate(
        total_deals=Count("deal", distinct=True)
    )
    available_categories = category_queryset.order_by("name")
    popular_categories = category_queryset.order_by("-total_deals", "name")[:8]

    recent_deals = (
        Deal.objects.select_related("merchant")
        .prefetch_related("categories")
        .order_by("-created_at")[:6]
    )

    if show_results:
        deal_filters = (
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(merchant__name__icontains=q)
            | Q(merchant__contact__icontains=q)
            | Q(categories__name__icontains=q)
        )

        discount_expression = Case(
            When(
                price_original__gt=0,
                then=ExpressionWrapper(
                    (F("price_original") - F("price_discount"))
                    / F("price_original")
                    * Decimal("100"),
                    output_field=FloatField(),
                ),
            ),
            default=Value(0.0),
            output_field=FloatField(),
        )

        deal_qs = (
            Deal.objects.select_related("merchant")
            .prefetch_related("categories")
            .filter(deal_filters)
        )

        if selected_categories:
            deal_qs = deal_qs.filter(categories__id__in=selected_categories)

        deal_qs = (
            deal_qs.annotate(
                score_title_exact=Case(
                    When(title__iexact=q, then=Value(8)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_title_prefix=Case(
                    When(title__istartswith=q, then=Value(5)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_title_part=Case(
                    When(title__icontains=q, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_description=Case(
                    When(description__icontains=q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_merchant=Case(
                    When(merchant__name__icontains=q, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_category=Case(
                    When(categories__name__icontains=q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                discount_rate=discount_expression,
            )
            .annotate(
                relevance=
                F("score_title_exact")
                + F("score_title_prefix")
                + F("score_title_part")
                + F("score_description")
                + F("score_merchant")
                + F("score_category")
            )
            .distinct()
        )

        if sort == "discount":
            deal_qs = deal_qs.order_by("-discount_rate", "-relevance", "title")
        elif sort == "new":
            deal_qs = deal_qs.order_by("-created_at", "-relevance", "title")
        else:
            sort = "relevance"
            deal_qs = deal_qs.order_by("-relevance", "title")

        paginator = Paginator(deal_qs, 10)
        deal_total = paginator.count

        if deal_total:
            page_number = request.GET.get("page")
            deals_page = paginator.get_page(page_number)

        merchants = (
            Merchant.objects.filter(
                Q(name__icontains=q) | Q(contact__icontains=q)
            )
            .annotate(
                score_name_exact=Case(
                    When(name__iexact=q, then=Value(4)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_name_prefix=Case(
                    When(name__istartswith=q, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                score_contact=Case(
                    When(contact__icontains=q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                deals_total=Count("deal", distinct=True),
            )
            .annotate(
                relevance=
                F("score_name_exact")
                + F("score_name_prefix")
                + F("score_contact")
            )
            .order_by("-relevance", "name")
        )
        merchant_total = merchants.count()

        categories = (
            Category.objects.filter(name__icontains=q)
            .annotate(deals_total=Count("deal", distinct=True))
            .order_by("name")
        )
        category_total = categories.count()

    context = {
        "q": q,
        "sort": sort,
        "deals": deals_page,
        "merchants": merchants,
        "categories": categories,
        "deal_total": deal_total,
        "merchant_total": merchant_total,
        "category_total": category_total,
        "selected_categories": selected_categories,
        "available_categories": available_categories,
        "popular_categories": popular_categories,
        "recent_deals": recent_deals,
        "filters_active": bool(selected_categories),
        "show_results": show_results,
        "query_too_short": query_too_short,
    }

    return render(request, "search.html", context)


def category(request, pk):
    """Страница категории с акциями"""
    category = get_object_or_404(Category, pk=pk)
    deals = Deal.objects.filter(categories=category)
    return render(request, "category.html", {
        "category": category,
        "deals": deals,
    })


def deal_detail(request, pk):
    """Детальная страница акции"""
    deal = get_object_or_404(Deal, pk=pk)
    is_fav = False
    if request.user.is_authenticated:
        is_fav = request.user in deal.favorited_by.all()

    return render(request, "deal_detail.html", {
        "deal": deal,
        "is_fav": is_fav,
    })


@login_required
def toggle_favorite(request, pk):
    """Добавить или убрать акцию из избранного"""
    deal = get_object_or_404(Deal, pk=pk)

    if request.user in deal.favorited_by.all():
        deal.favorited_by.remove(request.user)
    else:
        deal.favorited_by.add(request.user)

    return redirect("discounts:deal_detail", pk=deal.pk)


@login_required
def my_favorites(request):
    """Список избранных акций"""
    favorites = Deal.objects.filter(favorited_by=request.user)
    return render(request, "favorites.html", {"favorites": favorites})


def signup(request):
    """Регистрация нового пользователя"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("discounts:home")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})


@login_required
def deal_edit(request, pk):
    """Редактирование акции"""
    deal = get_object_or_404(Deal, pk=pk)

    if not request.user.is_staff:
        return redirect("discounts:deal_detail", pk=pk)

    if request.method == "POST":
        form = DealForm(request.POST, request.FILES, instance=deal)
        if form.is_valid():
            form.save()
            return redirect("discounts:deal_detail", pk=deal.pk)
    else:
        form = DealForm(instance=deal)

    return render(request, "deal_edit.html", {"form": form, "deal": deal})


@login_required
def deal_delete(request, pk):
    """Удаление акции"""
    deal = get_object_or_404(Deal, pk=pk)

    if not request.user.is_staff:
        return redirect("discounts:deal_detail", pk=pk)

    if request.method == "POST":
        deal.delete()
        return redirect("discounts:home")

    return render(request, "deal_confirm_delete.html", {"deal": deal})


@login_required
def deal_create(request):
    """Создание новой акции"""
    if not request.user.is_staff:
        return redirect("discounts:home")

    if request.method == "POST":
        form = DealForm(request.POST, request.FILES)
        if form.is_valid():
            deal = form.save()
            return redirect("discounts:deal_detail", pk=deal.pk)
    else:
        form = DealForm()

    return render(request, "deal_edit.html", {"form": form, "deal": None})


@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def update_all(request, pk):
    """AJAX-обновление полей акции (название, цены, дата, картинка, описание)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            deal = Deal.objects.get(pk=pk)

            deal.title = data.get('title', deal.title)

            def safe_decimal(value, default):
                try:
                    return Decimal(str(value)) if str(value).strip() != "" else default
                except Exception:
                    return default

            deal.price_original = safe_decimal(data.get('price_original'), deal.price_original)
            deal.price_discount = safe_decimal(data.get('price_discount'), deal.price_discount)

            expires = data.get('expires_at')
            if expires:
                deal.expires_at = expires

            deal.image_url = data.get('image_url', deal.image_url)
            deal.description = data.get('description', deal.description)

            deal.save()
            return JsonResponse({'status': 'ok'})

        except Exception as e:
            print("❌ Ошибка при обновлении:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=405)

from django.http import JsonResponse

@login_required
def toggle_favorite(request, pk):
    """Добавить или убрать акцию из избранного"""
    deal = get_object_or_404(Deal, pk=pk)

    if request.method in ["POST", "GET"]:
        if request.user in deal.favorited_by.all():
            deal.favorited_by.remove(request.user)
            result = {"status": "removed"}
        else:
            deal.favorited_by.add(request.user)
            result = {"status": "added"}

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(result)

        referer = request.META.get("HTTP_REFERER")
        if referer:
            return redirect(referer)
        return redirect("discounts:home")

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)