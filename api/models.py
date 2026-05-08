# /opt/gto_backend/api/models.py
from django.db import models

class Step(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    gender = models.CharField(max_length=1, choices=[('М', 'Мужской'), ('Ж', 'Женский')], verbose_name="Пол")
    age_min = models.IntegerField(default=6)
    age_max = models.IntegerField(default=70)

    # Лимиты для Золота (например: 4 обязательных, 2 выборных)
    gold_mandatory = models.IntegerField(default=4, verbose_name="Обязательных для Золота")
    gold_optional = models.IntegerField(default=2, verbose_name="Выборных для Золота")
    
    # Для Серебра и Бронзы лимиты обычно такие же или меньше
    silver_mandatory = models.IntegerField(default=4, verbose_name="Обязательных для Серебра")
    silver_optional = models.IntegerField(default=1, verbose_name="Выборных для Серебра")
    
    bronze_mandatory = models.IntegerField(default=4, verbose_name="Обязательных для Бронзы")
    bronze_optional = models.IntegerField(default=1, verbose_name="Выборных для Бронзы")

    def __str__(self):
        return f"{self.name} [{self.get_gender_display()}]"

class Exercise(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название упражнения")

    class Meta:
        verbose_name = "Упражнение"
        verbose_name_plural = "Упражнения"

    def __str__(self):
        return self.name

class Normative(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='norms', verbose_name="Ступень")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name="Упражнение")
    gold = models.FloatField(verbose_name="Золото")
    silver = models.FloatField(verbose_name="Серебро")
    bronze = models.FloatField(verbose_name="Бронза")
    is_mandatory = models.BooleanField(default=True, verbose_name="Обязательно")
    
    is_higher_better = models.BooleanField(
        default=False, 
        verbose_name="Больше = лучше (для отжиманий/прыжков)"
    )

    class Meta:
        verbose_name = "Норматив"
        verbose_name_plural = "Нормативы"

    def __str__(self):
        return f"{self.exercise.name} ({self.step})"


class ParticipantList(models.Model):
    """Модель для хранения списков участников"""
    name = models.CharField(max_length=200, verbose_name="Название списка")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Список участников"
        verbose_name_plural = "Списки участников"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Participant(models.Model):
    """Модель участника с привязкой к списку"""
    participant_list = models.ForeignKey(
        ParticipantList, 
        on_delete=models.CASCADE, 
        related_name='participants',
        verbose_name="Список"
    )
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    gender = models.CharField(
        max_length=1, 
        choices=[('М', 'Мужской'), ('Ж', 'Женский')], 
        verbose_name="Пол"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    uin = models.CharField(max_length=50, blank=True, null=True, verbose_name="УИН")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class TestResult(models.Model):
    """Модель для хранения результатов испытаний участников"""
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name="Участник"
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        verbose_name="Упражнение"
    )
    result = models.FloatField(verbose_name="Результат")
    result_date = models.DateField(verbose_name="Дата сдачи")
    medal = models.CharField(
        max_length=10,
        choices=[
            ('gold', 'Золото'),
            ('silver', 'Серебро'),
            ('bronze', 'Бронза'),
            ('none', 'Без знака')
        ],
        default='none',
        verbose_name="Знак отличия"
    )
    is_mandatory = models.BooleanField(default=False, verbose_name="Обязательное испытание")
    protocol_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер протокола")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления записи")

    class Meta:
        verbose_name = "Результат испытания"
        verbose_name_plural = "Результаты испытаний"
        ordering = ['-result_date', 'participant']
        # Убираем уникальность по exercise, чтобы участник мог сдавать одно упражнение несколько раз в разные даты
        # unique_together = ['participant', 'exercise', 'result_date']

    def __str__(self):
        medal_display = self.get_medal_display()
        return f"{self.participant} - {self.exercise}: {self.result} ({medal_display})"