from django.urls import path
from . import views

app_name = "discounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("category/<int:pk>/", views.category, name="category"),
    path("deal/<int:pk>/", views.deal_detail, name="deal_detail"),
    path("deal/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.my_favorites, name="my_favorites"),
    path("signup/", views.signup, name="signup"),  # регистрация
]
