"""education URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import os
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from apps.public.api import PublicFileAPIView
from apps.business_new.api import BusinessNewAPIView

router1 = DefaultRouter(trailing_slash=False)
router1.register('', PublicFileAPIView, base_name='')

router2 = DefaultRouter(trailing_slash=False)
router2.register('', BusinessNewAPIView, base_name='create_order')

urlpatterns = [
    path('client_api/', include('apps.urls'))
]

urlpatterns += static('/images/picvercode/',document_root=settings.PICVERCODE_PATH)
urlpatterns += static('/images/base/',document_root=settings.BASEPIC_PATH)
urlpatterns += static('/images/banner/',document_root=settings.BANNER_PATH)

