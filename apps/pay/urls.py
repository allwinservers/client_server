from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter(trailing_slash=False)
router.register('', PayAPIView, base_name='pay')

urlpatterns = [
    path('', include(router.urls))
]
