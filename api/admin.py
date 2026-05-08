from django.contrib import admin
from .models import Step, Exercise, Normative, ParticipantList, Participant, TestResult

admin.site.register(Step)
admin.site.register(Exercise)
admin.site.register(Normative)
admin.site.register(ParticipantList)
admin.site.register(Participant)
admin.site.register(TestResult)
