from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

from .models import Deal, Category, Coupon, Merchant


def home(request):
    """Главная страница с тремя блоками"""
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
        is_fav = Coupon.objects.filter(user=request.user, deal=deal).exists()

    return render(request, "deal_detail.html", {
        "deal": deal,
        "is_fav": is_fav,
    })


def toggle_favorite(request, pk):
    """Добавить/убрать акцию в избранное"""
    if not request.user.is_authenticated:
        return redirect("login")

    deal = get_object_or_404(Deal, pk=pk)
    coupon, created = Coupon.objects.get_or_create(
        user=request.user,
        deal=deal,
        defaults={"status": "active"}
    )

    if not created:
        coupon.delete()

    return redirect("discounts:deal_detail", pk=deal.pk)


def my_favorites(request):
    """Избранные акции"""
    if not request.user.is_authenticated:
        return redirect("login")

    coupons = Coupon.objects.filter(user=request.user, status="active")
    deals = [c.deal for c in coupons]

    return render(request, "favorites.html", {
        "deals": deals,
    })


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

from .forms import DealForm

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


def deal_delete(request, pk):
    """Удаление акции"""
    deal = get_object_or_404(Deal, pk=pk)

    if not request.user.is_staff:
        return redirect("discounts:deal_detail", pk=pk)

    if request.method == "POST":
        deal.delete()
        return redirect("discounts:home")

    return render(request, "deal_confirm_delete.html", {"deal": deal})