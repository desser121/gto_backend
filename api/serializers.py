from rest_framework import serializers
from .models import Step, Exercise, Normative, ParticipantList, Participant, TestResult


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


class TestResultSerializer(serializers.ModelSerializer):
    """Сериализатор для результатов испытаний"""
    participant_name = serializers.SerializerMethodField()
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    medal_display = serializers.CharField(source='get_medal_display', read_only=True)

    class Meta:
        model = TestResult
        fields = [
            'id', 'participant', 'participant_name', 'exercise', 'exercise_name',
            'result', 'result_date', 'medal', 'medal_display', 'is_mandatory',
            'protocol_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_participant_name(self, obj):
        return f"{obj.participant.last_name} {obj.participant.first_name}"


class ParticipantSerializer(serializers.ModelSerializer):
    """Сериализатор для участника"""
    age = serializers.SerializerMethodField()
    test_results = TestResultSerializer(many=True, read_only=True)

    class Meta:
        model = Participant
        fields = [
            'id', 'participant_list', 'first_name', 'last_name', 'middle_name',
            'birth_date', 'gender', 'email', 'phone', 'uin', 'created_at', 'age',
            'test_results'
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