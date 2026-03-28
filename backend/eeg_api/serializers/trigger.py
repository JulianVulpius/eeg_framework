from rest_framework import serializers
from eeg_api.models.trigger import TriggerDefinition, TriggerGroup, TriggerPair, TriggerHotkeyMapping

class TriggerDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerDefinition
        fields = ['id', 'name', 'trigger_character'] 

class TriggerGroupSerializer(serializers.ModelSerializer):
    triggers = serializers.PrimaryKeyRelatedField(
        queryset=TriggerDefinition.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = TriggerGroup
        fields = ['id', 'name', 'category', 'description', 'triggers']

class TriggerPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerPair
        fields = ['id', 'name', 'start_trigger', 'end_trigger']

class TriggerHotkeyMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerHotkeyMapping
        fields = '__all__'