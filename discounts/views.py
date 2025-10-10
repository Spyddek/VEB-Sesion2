from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal

from .models import Deal, Category, Merchant
from .forms import DealForm


# -------------------------------
# 🔹 Главная страница
# -------------------------------
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


# -------------------------------
# 🔹 Поиск
# -------------------------------
def search(request):
    """Поиск акций, магазинов и категорий"""
    q = request.GET.get("q", "").strip()
    deals, merchants, categories = [], [], []

    if q:
        deals = Deal.objects.filter(
            Q(title__icontains=q) |
            Q(merchant__name__icontains=q)
        )

        merchants = Merchant.objects.filter(
            Q(name__icontains=q) |
            Q(contact__icontains=q)
        )

        categories = Category.objects.filter(
            name__icontains=q
        )

    return render(request, "search.html", {
        "q": q,
        "deals": deals,
        "merchants": merchants,
        "categories": categories,
    })


# -------------------------------
# 🔹 Категория
# -------------------------------
def category(request, pk):
    """Страница категории с акциями"""
    category = get_object_or_404(Category, pk=pk)
    deals = Deal.objects.filter(categories=category)
    return render(request, "category.html", {
        "category": category,
        "deals": deals,
    })


# -------------------------------
# 🔹 Детальная страница акции
# -------------------------------
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


# -------------------------------
# 🔹 Избранное
# -------------------------------
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


# -------------------------------
# 🔹 Регистрация пользователей
# -------------------------------
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


# -------------------------------
# 🔹 Редактирование акции (форма)
# -------------------------------
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


# -------------------------------
# 🔹 Удаление акции
# -------------------------------
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


# -------------------------------
# 🔹 Создание новой акции
# -------------------------------
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


# -------------------------------
# 🔹 AJAX: обновление всех полей
# -------------------------------
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def update_all(request, pk):
    """AJAX-обновление полей акции (название, цены, дата, картинка, описание)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            deal = Deal.objects.get(pk=pk)

            deal.title = data.get('title', deal.title)

            # 🧩 Безопасное преобразование цен
            def safe_decimal(value, default):
                try:
                    return Decimal(str(value)) if str(value).strip() != "" else default
                except Exception:
                    return default

            deal.price_original = safe_decimal(data.get('price_original'), deal.price_original)
            deal.price_discount = safe_decimal(data.get('price_discount'), deal.price_discount)

            # 🧩 Обновляем дату
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

    # ✅ Работает и для GET, и для POST
    if request.method in ["POST", "GET"]:
        if request.user in deal.favorited_by.all():
            deal.favorited_by.remove(request.user)
            result = {"status": "removed"}
        else:
            deal.favorited_by.add(request.user)
            result = {"status": "added"}

        # ✅ Если это AJAX, возвращаем JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(result)

        # ✅ Иначе просто возвращаем на предыдущую страницу
        referer = request.META.get("HTTP_REFERER")
        if referer:
            return redirect(referer)
        return redirect("discounts:home")

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)