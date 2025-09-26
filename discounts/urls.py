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
    path("signup/", views.signup, name="signup"),

    # CRUD для акций
    path("deals/", views.deal_list, name="deal_list"),              # список всех акций
    path("deal/add/", views.deal_create, name="deal_create"),       # создание
    path("deal/<int:pk>/edit/", views.deal_update, name="deal_update"),  # редактирование
    path("deal/<int:pk>/delete/", views.deal_delete, name="deal_delete"), # удаление
]
