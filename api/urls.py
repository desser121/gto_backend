from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NormativeViewSet

router = DefaultRouter()
router.register(r'norms', NormativeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]