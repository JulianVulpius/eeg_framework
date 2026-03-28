from rest_framework import serializers
from eeg_api.models.recordings import EEGDataFile, HeartRateDataFile, GenericRecording

class EEGDataFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EEGDataFile
        fields = '__all__'

class HeartRateDataFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRateDataFile
        fields = '__all__'

class GenericRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericRecording
        fields = '__all__'