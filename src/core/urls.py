from django.urls import path, include, re_path

from core import views, constants

audiofiletype_url_param = r'(?P<audiofiletype>{}|{}|{})'.format(constants.SONG, constants.AUDIOBOOK, constants.PODCAST)
audiofileid_url_param = r'(?P<audiofileid>\d+)'

audiofileurlpatterns = [
    path("", views.AudioFileCreateAPIView.as_view(), name='create-audio-file'),
    re_path(
        r"^{}/{}/$".format(audiofiletype_url_param, audiofileid_url_param),
        views.AudioFileViewSet.as_view(
            actions={
                "put": "update",
                "patch": "partial_update",
                "get": "retrieve",
                "delete": "destroy",
            }
        ),
        name='common-actions-audio-file'
    ),
    re_path(
        r"^{}/$".format(audiofiletype_url_param),
        views.AudioFileViewSet.as_view(actions={"get": "list"}),
        name='list-audio-files'
    ),
]


urlpatterns = [
    path("audiofile/", include(audiofileurlpatterns)),
]
