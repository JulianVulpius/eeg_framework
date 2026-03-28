from rest_framework import viewsets
from eeg_api.models.subject import SubjectProfile
from eeg_api.serializers.subject import SubjectProfileSerializer

class SubjectProfileViewSet(viewsets.ModelViewSet):
    queryset = SubjectProfile.objects.all().order_by('id')
    serializer_class = SubjectProfileSerializer