from django.contrib import admin
from django.urls import path
from discounts.views import home, search

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("search/", search, name="search"),
]
