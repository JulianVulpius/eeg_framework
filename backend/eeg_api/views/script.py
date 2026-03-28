from rest_framework import viewsets
from eeg_api.models.script import CustomScriptLanguage, CustomScript, DataProcess, DataDisplay
from eeg_api.serializers.script import (
    CustomScriptLanguageSerializer, CustomScriptSerializer, 
    DataProcessSerializer, DataDisplaySerializer
)

class CustomScriptLanguageViewSet(viewsets.ModelViewSet):
    queryset = CustomScriptLanguage.objects.all().order_by('name')
    serializer_class = CustomScriptLanguageSerializer

class CustomScriptViewSet(viewsets.ModelViewSet):
    queryset = CustomScript.objects.all().order_by('-created_at')
    serializer_class = CustomScriptSerializer

class DataProcessViewSet(viewsets.ModelViewSet):
    queryset = DataProcess.objects.all().order_by('name')
    serializer_class = DataProcessSerializer

class DataDisplayViewSet(viewsets.ModelViewSet):
    queryset = DataDisplay.objects.all().order_by('name')
    serializer_class = DataDisplaySerializer