from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # 🔑 стандартные Django auth урлы (login, logout, password reset и т.д.)
    path("accounts/", include("django.contrib.auth.urls")),

    # твое приложение discounts
    path("", include("discounts.urls")),
]
