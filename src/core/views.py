from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core import mixins, serializers


class AudioFileCreateAPIView(generics.CreateAPIView, mixins.AudioFileModelSerializerMappingMixin):
    """Create an Audio File Record in the specified audio type"""

    serializer_class = serializers.AudioFileTypeSerializer

    def get_serializer_class(self):
        """Check which audiofiletype is passed and choose a serializer for the same from the defined mapping"""

        audiofiletype_serializer = self.serializer_class(data=self.request.data)
        audiofiletype_serializer.is_valid(raise_exception=True)
        audiofiletype = audiofiletype_serializer.validated_data['audiofiletype']
        return self.audio_type_serializer_model_mapping[audiofiletype]['serializer']

    def create(self, request, *args, **kwargs):
        """Create a record in table of the deduced audiofiletype"""

        serializer_class = self.get_serializer_class()
        self.kwargs.setdefault('context', self.get_serializer_context())

        metadata_field_name = 'audiofilemetadata'
        audiofilemetadata = request.data.get(metadata_field_name)

        if audiofilemetadata is None:
            raise ValidationError(detail={metadata_field_name: ['This field is required']})

        serializer = serializer_class(data=audiofilemetadata)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AudioFileViewSet(viewsets.ModelViewSet, mixins.AudioFileModelSerializerMappingMixin):
    """A Set of Views to Retieve, List, Update and Delete audiofiles of an audiotype"""

    http_method_names = ['get', 'put', 'patch', 'delete']
    lookup_url_kwarg = 'audiofileid'

    def get_queryset(self):
        """Select audiofiletype model based on the url paramter"""

        selected_model = self.audio_type_serializer_model_mapping[self.kwargs.get('audiofiletype')]['model']
        return selected_model.objects.all()

    def get_serializer_class(self):
        """Select audiofiletype serializer based on the url paramter"""

        return self.audio_type_serializer_model_mapping[self.kwargs.get('audiofiletype')]["serializer"]
