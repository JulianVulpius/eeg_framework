from rest_framework import serializers
from eeg_api.models.subject import SubjectProfile

class SubjectProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectProfile
        fields = '__all__'