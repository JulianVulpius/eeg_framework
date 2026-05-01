from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from eeg_api.models.device import DeviceModel, Manufacturer, EEGChannel, DeviceModelEEGChannel, FrequencyBand, DeviceInstance
from eeg_api.models.metadata import MetaDataGroup, MetaDataGroupInstance

class FrequencyBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequencyBand
        fields = '__all__'

class EEGChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EEGChannel
        fields = '__all__'

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'

class DeviceModelSerializer(serializers.ModelSerializer):
    is_locked = serializers.BooleanField(read_only=True, default=False)
    manufacturer_name = serializers.ReadOnlyField(source='manufacturer.name')
    
    channels = serializers.PrimaryKeyRelatedField(
        queryset=EEGChannel.objects.all(), many=True, required=False
    )
    channel_names = serializers.SerializerMethodField()

    hardware_specs_group_id = serializers.PrimaryKeyRelatedField(
        queryset=MetaDataGroup.objects.all(), write_only=True, required=False, allow_null=True
    )
    default_settings_group_id = serializers.PrimaryKeyRelatedField(
        queryset=MetaDataGroup.objects.all(), write_only=True, required=False, allow_null=True
    )

    current_hardware_specs_group_id = serializers.SerializerMethodField()
    current_default_settings_group_id = serializers.SerializerMethodField()

    class Meta:
        model = DeviceModel
        fields = [
            'id', 'name', 'manufacturer', 'manufacturer_name', 'category', 
            'is_eeg', 'channels', 'channel_names', 'is_archived', 'is_locked',
            'hardware_specs', 'default_settings',
            'hardware_specs_group_id', 'default_settings_group_id',
            'current_hardware_specs_group_id', 'current_default_settings_group_id'
        ]

    def get_channel_names(self, obj):
        return list(obj.channels.values_list('name', flat=True))

    def get_current_hardware_specs_group_id(self, obj):
        return obj.hardware_specs.group_id if obj.hardware_specs else None

    def get_current_default_settings_group_id(self, obj):
        return obj.default_settings.group_id if obj.default_settings else None

    def _handle_metadata_instance(self, group, current_instance, device_model):
        if not group:
            if current_instance:
                current_instance.delete()
            return None

        if current_instance:
            if current_instance.group_id == group.id:
                return current_instance
            else:
                current_instance.delete()

        return MetaDataGroupInstance.objects.create(
            group=group,
            creation_source=MetaDataGroupInstance.CreationSource.DEVICE,
            content_type=ContentType.objects.get_for_model(DeviceModel),
            object_id=device_model.id
        )

    def create(self, validated_data):
        channels = validated_data.pop('channels', [])
        hw_group = validated_data.pop('hardware_specs_group_id', None)
        ds_group = validated_data.pop('default_settings_group_id', None)

        device_model = DeviceModel.objects.create(**validated_data)

        if device_model.is_eeg:
            for channel in channels:
                DeviceModelEEGChannel.objects.create(device_model=device_model, eeg_channel=channel)

        if hw_group:
            device_model.hardware_specs = self._handle_metadata_instance(hw_group, None, device_model)
        if ds_group:
            device_model.default_settings = self._handle_metadata_instance(ds_group, None, device_model)
        
        device_model.save()
        return device_model

    def update(self, instance, validated_data):
        channels = validated_data.pop('channels', None)
        
        has_hw = 'hardware_specs_group_id' in validated_data
        hw_group = validated_data.pop('hardware_specs_group_id', None)
        
        has_ds = 'default_settings_group_id' in validated_data
        ds_group = validated_data.pop('default_settings_group_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if channels is not None:
            DeviceModelEEGChannel.objects.filter(device_model=instance).delete()
            if instance.is_eeg:
                for channel in channels:
                    DeviceModelEEGChannel.objects.create(device_model=instance, eeg_channel=channel)
        elif not getattr(instance, 'is_eeg', True):
            DeviceModelEEGChannel.objects.filter(device_model=instance).delete()

        if has_hw:
            instance.hardware_specs = self._handle_metadata_instance(hw_group, instance.hardware_specs, instance)
        if has_ds:
            instance.default_settings = self._handle_metadata_instance(ds_group, instance.default_settings, instance)

        instance.save()
        return instance

class DeviceInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceInstance
        fields = [
            'id', 'session', 'device_model', 'phase_config', 
            'metadata_overwrite_instance', 'final_channels', 'created_at'
        ]