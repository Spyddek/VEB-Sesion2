from django.urls import path
from . import views

app_name = "discounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("deal/<int:pk>/", views.deal_detail, name="deal_detail"),
    path("category/<int:cat_id>/", views.category_page, name="category"),
    path("search/", views.search, name="search"),
]
