from rest_framework import serializers
from eeg_api.models.subject import SubjectProfile, SubjectProfileInfoCategory, SubjectProfileInfo

class SubjectProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectProfile
        fields = '__all__'

class SubjectProfileInfoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectProfileInfoCategory
        fields = '__all__'

class SubjectProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectProfileInfo
        fields = '__all__'