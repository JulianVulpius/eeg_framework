import json
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from eeg_api.models import Component, ComponentType, ComponentCategory

class ComponentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentType
        fields = ['id', 'name', 'identifier', 'description']

class ComponentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentCategory
        fields = '__all__'

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ['id', 'name', 'category', 'component_type', 'description', 'parameter']

    def validate_parameter(self, value):
        """Ensures parameter field contains valid JSON string."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                raise ValidationError("Invalid JSON format for parameters.")
        return value