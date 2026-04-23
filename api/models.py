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