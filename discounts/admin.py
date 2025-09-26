from django.contrib import admin
from .models import Role, Merchant, Category, Deal, DealCategory, Coupon


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class DealCategoryInline(admin.TabularInline):
    model = DealCategory
    extra = 1


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact", "user")
    search_fields = ("name", "contact")
    list_filter = ("user",)
    raw_id_fields = ("user",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "merchant", "price_original", "price_discount", "get_discount_percent", "created_at")
    list_filter = ("merchant", "categories", "created_at")
    inlines = [DealCategoryInline]
    date_hierarchy = "created_at"
    search_fields = ("title",)
    raw_id_fields = ("merchant",)
    readonly_fields = ("created_at",)

    @admin.display(description="Скидка (%)")
    def get_discount_percent(self, obj):
        return obj.discount_percent()


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "id", "user", "deal", "status", "issued_at", "redeemed_at")
    list_filter = ("status", "issued_at", "redeemed_at")
    date_hierarchy = "issued_at"
    search_fields = ("code", "user__username", "deal__title")
    raw_id_fields = ("user", "deal")
    readonly_fields = ("issued_at",)
