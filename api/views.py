from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Normative, ParticipantList, Participant, Step, Exercise, TestResult
from .serializers import (
    NormativeSerializer, ParticipantListSerializer,
    ParticipantListCreateUpdateSerializer, ParticipantSerializer,
    TestResultSerializer
)
import openpyxl
from datetime import datetime
from io import BytesIO


class NormativeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Normative.objects.all()
    serializer_class = NormativeSerializer


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        participant_id = self.request.query_params.get('participant')
        if participant_id:
            queryset = queryset.filter(participant_id=participant_id)
        return queryset


class ParticipantListViewSet(viewsets.ModelViewSet):
    queryset = ParticipantList.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ParticipantListSerializer
        return ParticipantListCreateUpdateSerializer


class ParticipantViewSet(viewsets.ModelViewSet):
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
        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })


class ExportFederalTemplateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        participants_data = request.data.get('participants', [])
        exercise_names = request.data.get('exercise_names', [])
        region = request.data.get('region', 'Удмуртская Республика')
        center_name = request.data.get('center_name', '')

        if not participants_data:
            return Response({"error": "Нет данных участников"}, status=400)
        if not exercise_names:
            return Response({"error": "Нет названий упражнений"}, status=400)

        template_path = 'api/federal_template.xlsx'
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        today = datetime.now().date()

        ws['D4'] = region

        if center_name:
            ws['D8'] = center_name

        if participants_data:
            first = participants_data[0]
            age = self._calc_age(first.get('birthdate', ''))
            gender = first.get('gender', 'М')
            step = first.get('step', '')

            ws['F7'] = step
            ws['G7'] = 'мужской' if gender == 'М' else 'женский'
            ws['M7'] = f'« {today.day} »'
            ws['N7'] = self._month_name(today.month)
            ws['O7'] = f'{today.year} года'

        for i, name in enumerate(exercise_names):
            col = 5 + i
            ws.cell(row=12, column=col).value = name

        for idx, p in enumerate(participants_data):
            row = 13 + idx
            ws.cell(row=row, column=1).value = idx + 1

            fio = p.get('fio', '')
            ws.cell(row=row, column=2).value = fio
            ws.cell(row=row, column=4).value = p.get('uin', '')
            ws.cell(row=row, column=3).value = ''

            values = p.get('values', {})
            for i, ex_name in enumerate(exercise_names):
                col = 5 + i
                val = values.get(ex_name, '')
                ws.cell(row=row, column=col).value = val if val else ''

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = f"federal_template_{today.strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _calc_age(self, birthdate_str):
        if not birthdate_str:
            return 0
        try:
            bd = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            age = today.year - bd.year
            if (today.month, today.day) < (bd.month, bd.day):
                age -= 1
            return age
        except Exception:
            return 0

    def _month_name(self, m):
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return months.get(m, '')
