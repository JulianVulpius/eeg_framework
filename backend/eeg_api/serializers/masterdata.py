from rest_framework import serializers
from eeg_api.models import Location, LocationCategory, FrequencyBand, EEGChannel, Manufacturer

class LocationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationCategory
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

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