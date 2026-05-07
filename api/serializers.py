from rest_framework import serializers
from .models import Step, Exercise, Normative, ParticipantList, Participant


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


class ParticipantSerializer(serializers.ModelSerializer):
    """Сериализатор для участника"""
    age = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = [
            'id', 'participant_list', 'first_name', 'last_name', 'middle_name',
            'birth_date', 'gender', 'email', 'phone', 'created_at', 'age'
        ]
        read_only_fields = ['created_at']

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        age = today.year - obj.birth_date.year
        if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):
            age -= 1
        return age


class ParticipantListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка участников с вложенными участниками"""
    participants = ParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantList
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at',
            'participants', 'participant_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_participant_count(self, obj):
        return obj.participants.count()


class ParticipantListCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления списка участников"""
    class Meta:
        model = ParticipantList
        fields = ['id', 'name', 'description']