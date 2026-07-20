from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import ParticipantList, Participant, Exercise, TestResult
from .permissions import get_user_permissions
from .audit import log_action
from datetime import datetime


class SaveDashboardListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        perms, _ = get_user_permissions(request.user)
        if 'save_list' not in perms:
            return Response({'error': 'Нет прав на сохранение списков'}, status=403)

        list_id = request.data.get('list_id')
        list_name = request.data.get('list_name', 'Расчет знака')
        rows = request.data.get('rows', [])
        columns = request.data.get('columns', [])
        force_overwrite = request.data.get('force_overwrite', False)

        if not rows:
            return Response({'error': 'Нет данных'}, status=400)

        if not list_id:
            existing = ParticipantList.objects.filter(name=list_name).first()
            if existing and not force_overwrite:
                return Response({
                    'error': 'duplicate_name',
                    'existing_id': existing.id,
                    'existing_name': existing.name,
                    'existing_count': existing.participants.count(),
                }, status=409)
            elif existing and force_overwrite:
                list_id = existing.id

        if list_id:
            try:
                plist = ParticipantList.objects.get(id=list_id)
                plist.name = list_name
                plist.save()
            except ParticipantList.DoesNotExist:
                plist = ParticipantList.objects.create(name=list_name)
            plist.participants.all().delete()
        else:
            plist = ParticipantList.objects.create(name=list_name)

        for row in rows:
            fio = (row.get('fio') or '').strip()
            if not fio:
                continue

            parts = fio.split()
            last_name = parts[0] if len(parts) > 0 else ''
            first_name = parts[1] if len(parts) > 1 else ''
            middle_name = ' '.join(parts[2:]) if len(parts) > 2 else ''

            birthdate = row.get('birthdate', '')
            try:
                bd = datetime.strptime(birthdate, '%Y-%m-%d').date() if birthdate else datetime.now().date()
            except Exception:
                bd = datetime.now().date()

            participant = Participant.objects.create(
                participant_list=plist,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name if middle_name else None,
                birth_date=bd,
                gender=row.get('gender', 'М'),
                uin=row.get('uin', ''),
            )

            values = row.get('values', {})
            results = row.get('results', {})
            for col in columns:
                if not col:
                    continue
                val = values.get(col, '')
                grade = results.get(col)
                if val and val.strip():
                    exercise, _ = Exercise.objects.get_or_create(name=col)
                    medal = grade if grade in ('gold', 'silver', 'bronze') else 'none'
                    TestResult.objects.create(
                        participant=participant,
                        exercise=exercise,
                        result=float(val) if val else 0,
                        result_date=bd,
                        medal=medal,
                    )

        log_action(request.user, 'save_list', f'Сохранён список "{list_name}"', f'{plist.participants.count()} участников')

        return Response({
            'list_id': plist.id,
            'list_name': plist.name,
            'participants_count': plist.participants.count(),
        })
