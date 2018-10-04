"""binder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dns_server.views import *

router = DefaultRouter()
router.register(r'keys', KeyViewSet, base_name='dns-keys')
router.register(r'zones', ZoneViewSet, base_name='dns-zone')
router.register(r'records', RecordViewSet, base_name='dns-record')
router.register(r'server', ServerViewSet, base_name='dns-server')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dns/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]
