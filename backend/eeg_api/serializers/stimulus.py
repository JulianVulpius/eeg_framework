from rest_framework import serializers
from eeg_api.models.stimulus import Stimulus, StimulusPlaylist, StimulusPlaylistStimulus

class StimulusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stimulus
        fields = '__all__'

class StimulusPlaylistSerializer(serializers.ModelSerializer):
    stimuli = serializers.PrimaryKeyRelatedField(
        queryset=Stimulus.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = StimulusPlaylist
        fields = ['id', 'name', 'category', 'stimuli']

    def create(self, validated_data):
        stimuli_data = validated_data.pop('stimuli', [])
        playlist = StimulusPlaylist.objects.create(**validated_data)
        for index, stimulus in enumerate(stimuli_data):
            StimulusPlaylistStimulus.objects.create(
                playlist=playlist,
                stimulus=stimulus,
                order=index + 1
            )
        return playlist

    def update(self, instance, validated_data):
        if 'stimuli' in validated_data:
            stimuli_data = validated_data.pop('stimuli')
            StimulusPlaylistStimulus.objects.filter(playlist=instance).delete()
            for index, stimulus in enumerate(stimuli_data):
                StimulusPlaylistStimulus.objects.create(
                    playlist=instance,
                    stimulus=stimulus,
                    order=index + 1
                )
        
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance