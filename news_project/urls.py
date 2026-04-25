"""
URL configuration for News Application project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('articles.api.urls')),
    path('', include('articles.urls')),
]
