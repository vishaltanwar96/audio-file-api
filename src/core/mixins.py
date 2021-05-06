from core import models, serializers, constants


class AudioFileModelSerializerMappingMixin:
    """Mapping of Audio File Type and their corresponding serializer and model mapping"""

    audio_type_serializer_model_mapping = {
        constants.SONG: {
            'serializer': serializers.SongSerializer,
            'model': models.Song
        },
        constants.PODCAST: {
            'serializer': serializers.PodcastSerializer,
            'model': models.Podcast
        },
        constants.AUDIOBOOK: {
            'serializer': serializers.AudioBookSerializer,
            'model': models.AudioBook
        }
    }
