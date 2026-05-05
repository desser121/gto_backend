from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token # Импорт для токенов
from .views import NormativeViewSet, CurrentUserView

router = DefaultRouter()
router.register(r'norms', NormativeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Добавляем эндпоинт для логина
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('user/', CurrentUserView.as_view(), name='current_user'),
]
