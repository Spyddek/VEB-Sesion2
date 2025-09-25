from django.contrib import admin
from .models import Role, User, Merchant, Category, Deal, DealCategory, Coupon


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role", "created_at")
    list_filter = ("role", "created_at")
    date_hierarchy = "created_at"
    search_fields = ("email",)
    list_display_links = ("email",)
    raw_id_fields = ("role",)
    readonly_fields = ("created_at",)


class DealCategoryInline(admin.TabularInline):
    model = DealCategory
    extra = 1


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact", "user", "created_at")
    search_fields = ("name", "contact")
    list_filter = ("created_at",)
    raw_id_fields = ("user",)
    readonly_fields = ("created_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "merchant",
        "price_original",
        "price_discount",
        "discount_percent",
        "created_at",
    )
    list_filter = ("merchant", "categories", "created_at")
    inlines = [DealCategoryInline]
    date_hierarchy = "created_at"
    search_fields = ("title",)
    readonly_fields = ("created_at",)

    @admin.display(description="Скидка (%)")
    def discount_percent(self, obj):
        return obj.discount_percent()


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "user", "deal", "status", "issued_at", "redeemed_at")
    list_filter = ("status", "issued_at", "redeemed_at")
    date_hierarchy = "issued_at"
    search_fields = ("code", "user__email", "deal__title")
    raw_id_fields = ("user", "deal")
    readonly_fields = ("issued_at",)
