"""
URL configuration for reseller project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import path, include


def error_403_handler(request: HttpRequest, exception=None):
    return render(request=request, template_name="unauthenticated/pages/403.html")


def error_404_handler(request: HttpRequest, exception=None):
    return render(request=request, template_name="unauthenticated/pages/404.html")


def error_500_handler(request: HttpRequest, exception=None):
    return render(request=request, template_name="unauthenticated/pages/500.html")


handler403 = error_403_handler
handler404 = error_404_handler
handler500 = error_500_handler

urlpatterns = [
    path("", include("unauthenticated.urls")),
    path("db/", admin.site.urls),
    path("internal/", include("internal.urls")),
]
