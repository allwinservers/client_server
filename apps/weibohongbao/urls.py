from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter(trailing_slash=False)
router.register('', WeiBoAPIView, base_name='wb')

urlpatterns = [
    path('', include(router.urls))
]
