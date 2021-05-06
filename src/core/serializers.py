from core import models, constants

from rest_framework import serializers


class SongSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Song
        fields = '__all__'


class PodcastSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Podcast
        fields = '__all__'


class AudioBookSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.AudioBook
        fields = '__all__'


class AudioFileTypeSerializer(serializers.Serializer):

    audiofiletype = serializers.ChoiceField(choices=[constants.AUDIOBOOK, constants.SONG, constants.PODCAST])
