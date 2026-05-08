from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Normative, ParticipantList, Participant, Step, Exercise, TestResult
from .serializers import NormativeSerializer, ParticipantListSerializer, ParticipantListCreateUpdateSerializer, ParticipantSerializer, TestResultSerializer
import openpyxl
from datetime import datetime
from io import BytesIO


class NormativeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Normative.objects.all()
    serializer_class = NormativeSerializer


class TestResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления результатами испытаний.
    GET /api/test-results/ - получить все результаты (с фильтрацией по ?participant={id})
    POST /api/test-results/ - создать новый результат
    GET /api/test-results/{id}/ - получить детали результата
    PUT/PATCH /api/test-results/{id}/ - обновить результат
    DELETE /api/test-results/{id}/ - удалить результат
    """
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        participant_id = self.request.query_params.get('participant')
        if participant_id:
            queryset = queryset.filter(participant_id=participant_id)
        return queryset


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


class ExportFederalTemplateView(APIView):
    """
    Экспорт данных в федеральный шаблон GTO.
    POST /api/export-federal-template/
    Body: {"participant_list_id": <id>}
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        participant_list_id = request.data.get('participant_list_id')
        
        if not participant_list_id:
            return Response(
                {"error": "Необходимо указать participant_list_id"}, 
                status=400
            )
        
        try:
            participant_list = ParticipantList.objects.get(id=participant_list_id)
        except ParticipantList.DoesNotExist:
            return Response(
                {"error": "Список участников не найден"}, 
                status=404
            )
        
        participants = participant_list.participants.all()
        
        if not participants.exists():
            return Response(
                {"error": "Список участников пуст"}, 
                status=400
            )
        
        # Загружаем шаблон
        template_path = 'api/federal_template.xlsx'
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active
        
        # Определяем ступень и пол по первому участнику (для простоты)
        # В реальном проекте нужно определять по всем участникам или передавать параметры
        first_participant = participants.first()
        
        # Вычисляем возраст и определяем ступень
        today = datetime.now().date()
        age = today.year - first_participant.birth_date.year
        if (today.month, today.day) < (first_participant.birth_date.month, first_participant.birth_date.day):
            age -= 1
        
        # Определяем ступень по возрасту
        step = self._get_step_by_age(age, first_participant.gender)
        
        # Заполняем шапку протокола
        ws['D4'] = 'Удмуртская Республика'  # Регион (можно сделать настраиваемым)
        ws.cell(row=6, column=1).value = f'Сводный протокол выполнения государственных требований к физической подготовленности граждан Российской Федерации - ступени {step}'
        ws.cell(row=7, column=6).value = step  # ступень
        ws.cell(row=7, column=7).value = 'мужской' if first_participant.gender == 'М' else 'женский'  # пол
        ws.cell(row=7, column=13).value = str(today.day)  # день
        ws.cell(row=7, column=14).value = self._get_month_name(today.month)  # месяц
        ws.cell(row=7, column=15).value = str(today.year)  # год
        ws.cell(row=8, column=4).value = participant_list.name  # Наименование центра тестирования
        ws.cell(row=9, column=4).value = ''  # Адрес (можно добавить в модель ParticipantList)
        
        # Получаем упражнения для данной ступени
        exercises = self._get_exercises_for_step(step, first_participant.gender)
        
        # Заполняем данные участников
        start_row = 13  # Первая строка для данных
        for idx, participant in enumerate(participants, start=1):
            row_num = start_row + idx - 1
            
            # № п/п
            ws.cell(row=row_num, column=1).value = idx
            
            # Ф.И.О.
            full_name = f"{participant.last_name} {participant.first_name}"
            if participant.middle_name:
                full_name += f" {participant.middle_name}"
            ws.cell(row=row_num, column=2).value = full_name
            
            # Спортивное звание (пока пусто, можно добавить в модель)
            ws.cell(row=row_num, column=3).value = ''
            
            # УИН
            ws.cell(row=row_num, column=4).value = participant.uin or ''
            
            # Результаты испытаний (колонки E-O, 11 колонок)
            # Получаем нормативы для участника
            norms = self._get_participant_normatives(participant, step, exercises)
            
            for col_idx, exercise in enumerate(exercises[:11], start=5):  # E=5, максимум 11 колонок
                result = norms.get(exercise.id, '')
                ws.cell(row=row_num, column=col_idx).value = result
        
        # Сохраняем в буфер
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        # Формируем имя файла
        filename = f"federal_template_{participant_list.name}_{today.strftime('%Y%m%d')}.xlsx"
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def _get_step_by_age(self, age, gender):
        """Определяет ступень по возрасту и полу"""
        try:
            step = Step.objects.filter(age_min__lte=age, age_max__gte=age, gender=gender).first()
            if step:
                return step.name
        except:
            pass
        
        # Fallback по возрастным группам
        if age <= 7:
            return "I (6-7 лет)"
        elif age <= 9:
            return "II (8-9 лет)"
        elif age <= 11:
            return "III (10-11 лет)"
        elif age <= 13:
            return "IV (12-13 лет)"
        elif age <= 15:
            return "V (14-15 лет)"
        elif age <= 17:
            return "VI (16-17 лет)"
        elif age <= 19:
            return "VII (18-19 лет)"
        elif age <= 24:
            return "VIII (20-24 лет)"
        elif age <= 29:
            return "IX (25-29 лет)"
        elif age <= 34:
            return "X (30-34 лет)"
        elif age <= 39:
            return "XI (35-39 лет)"
        elif age <= 44:
            return "XII (40-44 лет)"
        elif age <= 49:
            return "XIII (45-49 лет)"
        elif age <= 54:
            return "XIV (50-54 лет)"
        elif age <= 59:
            return "XV (55-59 лет)"
        elif age <= 64:
            return "XVI (60-64 лет)"
        elif age <= 69:
            return "XVII (65-69 лет)"
        else:
            return "XVIII (70-100 лет)"
    
    def _get_month_name(self, month):
        """Возвращает название месяца на русском"""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return months.get(month, '')
    
    def _get_exercises_for_step(self, step_name, gender):
        """Получает список упражнений для данной ступени"""
        try:
            step = Step.objects.filter(name=step_name, gender=gender).first()
            if step:
                # Получаем уникальные упражнения из нормативов для этой ступени
                norms = Normative.objects.filter(step=step).select_related('exercise')
                exercises = []
                seen = set()
                for norm in norms:
                    if norm.exercise.id not in seen:
                        exercises.append(norm.exercise)
                        seen.add(norm.exercise.id)
                return exercises[:11]  # Максимум 11 упражнений для колонок E-O
        except:
            pass
        
        # Fallback - первые 11 упражнений
        return list(Exercise.objects.all()[:11])
    
    def _get_participant_normatives(self, participant, step_name, exercises):
        """
        Получает результаты участника по упражнениям.
        Использует модель TestResult для получения реальных результатов.
        Возвращает ЛУЧШИЙ результат по каждому упражнению (если их несколько).
        """
        results = {}
        
        # Получаем все результаты испытаний для данного участника
        test_results = TestResult.objects.filter(
            participant=participant,
            exercise__in=exercises
        ).select_related('exercise')
        
        # Группируем результаты по упражнениям и выбираем лучший
        exercise_results = {}
        for test_result in test_results:
            ex_id = test_result.exercise.id
            
            if ex_id not in exercise_results:
                exercise_results[ex_id] = []
            exercise_results[ex_id].append(test_result)
        
        # Для каждого упражнения выбираем лучший результат
        for ex_id, result_list in exercise_results.items():
            # Находим упражнение чтобы узнать is_higher_better
            exercise = result_list[0].exercise
            norm = Normative.objects.filter(
                exercise=exercise,
                step__name=step_name
            ).first()
            
            is_higher_better = norm.is_higher_better if norm else False
            
            # Сортируем результаты и берем лучший
            if is_higher_better:
                # Чем больше значение, тем лучше (отжимания, прыжки)
                best_result = max(result_list, key=lambda x: x.result)
            else:
                # Чем меньше значение, тем лучше (бег)
                best_result = min(result_list, key=lambda x: x.result)
            
            results[ex_id] = best_result.result
        
        # Для упражнений без результата ставим прочерк
        for exercise in exercises:
            if exercise.id not in results:
                results[exercise.id] = ''
        
        return results
