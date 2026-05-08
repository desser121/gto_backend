from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token # Импорт для токенов
from .views import NormativeViewSet, CurrentUserView, ParticipantListViewSet, ParticipantViewSet, ExportFederalTemplateView

router = DefaultRouter()
router.register(r'norms', NormativeViewSet)
router.register(r'participant-lists', ParticipantListViewSet)
router.register(r'participants', ParticipantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Добавляем эндпоинт для логина
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('user/', CurrentUserView.as_view(), name='current_user'),
    # Экспорт в федеральный шаблон
    path('export-federal-template/', ExportFederalTemplateView.as_view(), name='export_federal_template'),
]
