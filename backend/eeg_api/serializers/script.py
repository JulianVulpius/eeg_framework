from rest_framework import serializers
from eeg_api.models.script import (
    CustomScriptLanguage, CustomScript, DataProcess,
    DataProcessCustomScript, DataDisplay, DataDisplayCustomScript
)

class CustomScriptLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomScriptLanguage
        fields = '__all__'

class CustomScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomScript
        fields = '__all__'

class DataProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcess
        fields = '__all__'

class DataDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDisplay
        fields = '__all__'