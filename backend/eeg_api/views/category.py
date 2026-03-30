from django.http import Http404
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer
from eeg_api.models import (
    MetaDataCategory, StimulusCategory, ComponentCategory,
    CustomScriptCategory, DataProcessCategory, DataDisplayCategory,
    MetaDataGroupCategory, DeviceModelCategory, PageCategory, PageGroupCategory, 
    EventCategory, TriggerGroupCategory, LocationCategory, PlaylistCategory, ManufacturerCategory
)

# maps the vue frontend url slugs to django models
CATEGORY_MODEL_MAP = {
    'metadata': MetaDataCategory,
    'stimulus': StimulusCategory,
    'component': ComponentCategory,
    'custom-script': CustomScriptCategory,
    'data-process': DataProcessCategory,
    'data-display': DataDisplayCategory,
    'metadata-group': MetaDataGroupCategory,
    'device-model': DeviceModelCategory,
    'page': PageCategory,
    'page-group': PageGroupCategory,
    'event': EventCategory,
    'trigger-group': TriggerGroupCategory,
    'location': LocationCategory,
    'playlist': PlaylistCategory,
    'manufacturer': ManufacturerCategory,
}

# single api endpoint for all category tables
class GenericCategoryViewSet(viewsets.ModelViewSet):
    def get_model_class(self):
        table_name = self.kwargs.get('table_name')
        model_class = CATEGORY_MODEL_MAP.get(table_name)
        if not model_class:
            raise Http404(f"Table mapping for '{table_name}' not found.")
        return model_class

    def get_queryset(self):
        model_class = self.get_model_class()
        # returns all rows for the requested table
        return model_class.objects.all().order_by('id')

    def get_serializer_class(self):
        model_class = self.get_model_class()

        # dynamically create a serializer for the requested model
        class DynamicCategorySerializer(ModelSerializer):
            class Meta:
                model = model_class
                fields = ['id', 'name', 'description']

        return DynamicCategorySerializer