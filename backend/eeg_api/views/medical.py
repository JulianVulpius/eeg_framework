from rest_framework import viewsets
from eeg_api.models.medical import MedicalHistory, SubjectMedicalHistory
from eeg_api.serializers.medical import MedicalHistorySerializer, SubjectMedicalHistorySerializer

class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.all().order_by('-created_at')
    serializer_class = MedicalHistorySerializer

class SubjectMedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = SubjectMedicalHistory.objects.all().order_by('id')
    serializer_class = SubjectMedicalHistorySerializer