import os
from rest_framework import serializers
from eeg_api.models.media import MediaAsset

class MediaAssetSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(write_only=True, required=False)
    file_exists = serializers.SerializerMethodField() 

    class Meta:
        model = MediaAsset
        fields = '__all__'

    def get_file_exists(self, obj):
        if obj.file and hasattr(obj.file, 'path'):
            return os.path.isfile(obj.file.path)
        return False

    def create(self, validated_data):
        event_name = validated_data.pop('event_name', 'general')
        file_obj = validated_data.pop('file', None)
        instance = MediaAsset(**validated_data)
        instance.event_name_for_path = event_name
        
        if file_obj:
            instance.file = file_obj
            
        instance.save()
        return instance