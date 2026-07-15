from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    NormativeViewSet, CurrentUserView, ParticipantListViewSet,
    ParticipantViewSet, ExportFederalTemplateView, TestResultViewSet
)
from .save_list_view import SaveDashboardListView

router = DefaultRouter()
router.register(r'norms', NormativeViewSet)
router.register(r'participant-lists', ParticipantListViewSet)
router.register(r'participants', ParticipantViewSet)
router.register(r'test-results', TestResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('user/', CurrentUserView.as_view(), name='current_user'),
    path('export-federal-template/', ExportFederalTemplateView.as_view(), name='export_federal_template'),
    path('save-list/', SaveDashboardListView.as_view(), name='save_dashboard_list'),
]
