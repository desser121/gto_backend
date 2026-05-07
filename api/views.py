from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Normative, ParticipantList, Participant
from .serializers import NormativeSerializer, ParticipantListSerializer, ParticipantListCreateUpdateSerializer, ParticipantSerializer


class NormativeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Normative.objects.all()
    serializer_class = NormativeSerializer


class ParticipantListViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления списками участников.
    GET /api/participant-lists/ - получить все списки
    POST /api/participant-lists/ - создать новый список
    GET /api/participant-lists/{id}/ - получить детали списка с участниками
    PUT/PATCH /api/participant-lists/{id}/ - обновить список
    DELETE /api/participant-lists/{id}/ - удалить список
    """
    queryset = ParticipantList.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ParticipantListSerializer
        return ParticipantListCreateUpdateSerializer


class ParticipantViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления участниками.
    GET /api/participants/ - получить всех участников (с фильтрацией по ?participant_list={id})
    POST /api/participants/ - создать нового участника
    GET /api/participants/{id}/ - получить детали участника
    PUT/PATCH /api/participants/{id}/ - обновить участника
    DELETE /api/participants/{id}/ - удалить участника
    """
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        participant_list_id = self.request.query_params.get('participant_list')
        if participant_list_id:
            queryset = queryset.filter(participant_list_id=participant_list_id)
        return queryset


class CurrentUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        )
