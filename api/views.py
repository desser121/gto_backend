from rest_framework import viewsets
from .models import Normative
from .serializers import NormativeSerializer

class NormativeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Normative.objects.all()
    serializer_class = NormativeSerializer
