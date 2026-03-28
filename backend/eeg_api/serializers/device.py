from rest_framework import serializers
from eeg_api.models.device import DeviceModel, Manufacturer, EEGChannel, DeviceModelEEGChannel, FrequencyBand

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
    channels = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    assigned_channels = serializers.SerializerMethodField(read_only=True)
    channel_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DeviceModel
        fields = ['id', 'name', 'manufacturer', 'category', 'is_eeg', 'channels', 'assigned_channels', 'channel_names']

    def get_assigned_channels(self, obj):
        return [c.id for c in obj.channels.all()]

    def get_channel_names(self, obj):
        return ", ".join([c.name for c in obj.channels.all()])

    def create(self, validated_data):
        channels_data = validated_data.pop('channels', [])
        device_model = DeviceModel.objects.create(**validated_data)
        
        for channel_id in channels_data:
            DeviceModelEEGChannel.objects.create(
                device_model=device_model, 
                eeg_channel_id=channel_id
            )
        return device_model

    def update(self, instance, validated_data):
        if 'channels' in validated_data:
            channels_data = validated_data.pop('channels')
            DeviceModelEEGChannel.objects.filter(device_model=instance).delete()
            for channel_id in channels_data:
                DeviceModelEEGChannel.objects.create(
                    device_model=instance, 
                    eeg_channel_id=channel_id
                )
        
        instance.name = validated_data.get('name', instance.name)
        instance.manufacturer = validated_data.get('manufacturer', instance.manufacturer)
        instance.category = validated_data.get('category', instance.category)
        instance.is_eeg = validated_data.get('is_eeg', instance.is_eeg)
        instance.save()
        return instance