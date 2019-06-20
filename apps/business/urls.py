from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter(trailing_slash=False)
router.register('', BusinessAPIView, base_name='business')

urlpatterns = [
    path('', include(router.urls))
]