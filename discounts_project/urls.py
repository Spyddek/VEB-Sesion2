from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from discounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
]

path('search/', views.search, name='search'),

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('discounts.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)