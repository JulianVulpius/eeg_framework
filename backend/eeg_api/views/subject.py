from rest_framework import viewsets
from eeg_api.models.subject import SubjectProfile, SubjectProfileInfoCategory, SubjectProfileInfo
from eeg_api.serializers.subject import (
    SubjectProfileSerializer, 
    SubjectProfileInfoCategorySerializer, 
    SubjectProfileInfoSerializer
)

class SubjectProfileViewSet(viewsets.ModelViewSet):
    queryset = SubjectProfile.objects.all().order_by('id')
    serializer_class = SubjectProfileSerializer

class SubjectProfileInfoCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubjectProfileInfoCategory.objects.all().order_by('name')
    serializer_class = SubjectProfileInfoCategorySerializer

class SubjectProfileInfoViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectProfileInfoSerializer

    def get_queryset(self):
        queryset = SubjectProfileInfo.objects.all().order_by('-created_at')
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset