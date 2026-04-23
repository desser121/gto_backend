from rest_framework import serializers
from .models import Step, Exercise, Normative


class NormativeSerializer(serializers.ModelSerializer):
    # Вытягиваем названия вместо просто ID
    step_name = serializers.CharField(source='step.name', read_only=True)
    step_gender = serializers.CharField(source='step.gender', read_only=True)
    step_age_min = serializers.IntegerField(source='step.age_min', read_only=True)
    step_age_max = serializers.IntegerField(source='step.age_max', read_only=True)
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)

    class Meta:
        model = Normative
        fields = [
            'id', 'step_name', 'step_gender', 'step_age_min', 'step_age_max', 
            'exercise_name', 'gold', 'silver', 'bronze', 'is_mandatory', 
            'is_higher_better' 
        ]