from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter(trailing_slash=False)
router.register('', OrderAPIView, base_name='order')

urlpatterns = [
    path('', include(router.urls))
]