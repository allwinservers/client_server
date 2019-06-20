from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter(trailing_slash=False)
router.register('', DataCountAPIView, base_name='datacount')

urlpatterns = [
    path('', include(router.urls))
]