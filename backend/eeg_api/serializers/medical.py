from rest_framework import serializers
from eeg_api.models.medical import MedicalHistory, SubjectMedicalHistory

class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = '__all__'

class SubjectMedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectMedicalHistory
        fields = '__all__'