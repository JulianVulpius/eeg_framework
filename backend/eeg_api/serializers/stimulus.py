from rest_framework import serializers
from eeg_api.models.stimulus import Stimulus, Playlist, PlaylistStimulus

class StimulusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stimulus
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    stimuli = serializers.PrimaryKeyRelatedField(
        queryset=Stimulus.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'category', 'description', 'stimuli']

    def create(self, validated_data):
        stimuli_data = validated_data.pop('stimuli', [])
        playlist = Playlist.objects.create(**validated_data)
        for index, stimulus in enumerate(stimuli_data):
            PlaylistStimulus.objects.create(
                playlist=playlist,
                stimulus=stimulus,
                order=index + 1
            )
        return playlist

    def update(self, instance, validated_data):
        stimuli_data = validated_data.pop('stimuli', None)
        instance = super().update(instance, validated_data)

        if stimuli_data is not None:
            PlaylistStimulus.objects.filter(playlist=instance).delete()
            for index, stimulus in enumerate(stimuli_data):
                PlaylistStimulus.objects.create(
                    playlist=instance,
                    stimulus=stimulus,
                    order=index + 1
                )
        
        return instance