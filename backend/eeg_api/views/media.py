from rest_framework import viewsets
from eeg_api.models.media import MediaAsset
from eeg_api.serializers.media import MediaAssetSerializer

class MediaAssetViewSet(viewsets.ModelViewSet):
    queryset = MediaAsset.objects.all().order_by('-created_at')
    serializer_class = MediaAssetSerializer