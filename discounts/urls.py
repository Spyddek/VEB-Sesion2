from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('discounts/', views.discounts_list, name='discounts_list'),
]