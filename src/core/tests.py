import string
import random

from rest_framework import status
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from core.constants import PODCAST, SONG, AUDIOBOOK
from core.models import AudioBook, Song, Podcast
from core.serializers import PodcastSerializer, AudioBookSerializer, SongSerializer


def create_audiofile_objects():

    song = Song.objects.create(name='Rolex', duration=240)
    podcast = Podcast.objects.create(
        name='The Python Podcast',
        duration=240,
        participants=['Vishal', 'Rohit'],
        host='Somebody'
    )
    audiobook = AudioBook.objects.create(
        name='Some Audiobook',
        duration=240,
        narrator='Vishal',
        author='Someone'
    )
    return song, podcast, audiobook


class AudioFileCreateTests(APITestCase):

    def setUp(self):
        self.url = reverse('create-audio-file')

    def test_create_audio_file_without_data(self):

        response = self.client.post(path=self.url, data={})
        self.assertEqual(response.data, {"audiofiletype": ["This field is required."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_with_wrong_audiotype_choice(self):

        response = self.client.post(path=self.url, data={'audiofiletype': 'somethingrandom'})
        self.assertEqual(response.data, {"audiofiletype": ["\"somethingrandom\" is not a valid choice."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_without_audio_metadata(self):

        for audio_type in [AUDIOBOOK, SONG, PODCAST]:
            response = self.client.post(path=self.url, data={'audiofiletype': audio_type})
            self.assertEqual(response.data, {"audiofilemetadata": ["This field is required"]})
            self.assertEqual(response.status_code, 400)

    def test_create_song_with_empty_metadata_body(self):

        response = self.client.post(path=self.url, data={"audiofiletype": SONG, "audiofilemetadata": {}})
        self.assertEqual(response.data, {"name": ["This field is required."], "duration": ["This field is required."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_metadata_field_data_type_validation(self):

        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": SONG,
                "audiofilemetadata": {
                    "name": random.choice([{'k': 'v'}, [123]]),
                    "duration": random.choice(['ajsdk', 12.091283, {'k': 'v'}, [123]])
                }
            }
        )
        self.assertEqual(response.data, {"name": ["Not a valid string."], "duration": ["A valid integer is required."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_metadata_field_validation(self):

        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": SONG,
                "audiofilemetadata": {
                    "name": "".join(random.choices(f'{string.ascii_uppercase}{string.ascii_lowercase}', k=101)),
                    "duration": 2147483648  # Since it is practically not possible for an audio to be of that length
                }
            }
        )
        self.assertEqual(response.data, {
            "name": [
                "Ensure this field has no more than 100 characters."
            ],
            "duration": [
                "Ensure this value is less than or equal to 2147483647."
            ]
        })
        self.assertEqual(response.status_code, 400)

    def test_create_song(self):

        song_name = 'Rolex'
        song_duration = 249
        now = timezone.now()
        response = self.client.post(path=self.url, data={
            "audiofiletype": SONG,
            "audiofilemetadata": {
                "name": song_name,
                "duration": song_duration
            }
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, SongSerializer(instance=Song.objects.get()).data)
        self.assertGreater(parse_datetime(response.data.get('uploaded_time')), now)
        self.assertEqual(Song.objects.count(), 1)

    def test_create_podcast_with_empty_metadata_body(self):

        response = self.client.post(path=self.url, data={"audiofiletype": PODCAST, "audiofilemetadata": {}})
        self.assertEqual(
            response.data,
            {
                "name": ["This field is required."],
                "duration": ["This field is required."],
                "host": ["This field is required."]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_podcast_metadata_field_data_type_validation(self):

        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": PODCAST,
                "audiofilemetadata": {
                    "name": random.choice([{'k': 'v'}, [123]]),
                    "duration": random.choice(['ajsdk', 12.091283, {'k': 'v'}, [123]]),
                    "host": random.choice([{'k': 'v'}, [123]]),
                    "participants": {'k': 'v'}
                }
            }
        )
        self.assertEqual(
            response.data,
            {
                "name": ["Not a valid string."],
                "duration": ["A valid integer is required."],
                "host": ["Not a valid string."],
                "participants": ["Expected a list of items but got type \"dict\"."]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_podcast_metadata_field_validation_participants_more_than_ten(self):

        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": PODCAST,
                "audiofilemetadata": {
                    "name": "".join(random.choices(f'{string.ascii_uppercase}{string.ascii_lowercase}', k=101)),
                    "duration": 2147483648,
                    "participants": [
                        "".join(random.choices(f'{string.ascii_uppercase}{string.ascii_lowercase}', k=99))
                        for _ in range(11)
                    ],
                    "host": "".join(random.choices(f'{string.ascii_uppercase}{string.ascii_lowercase}', k=101))
                }
            }
        )
        self.assertEqual(
            response.data,
            {
                "name": ["Ensure this field has no more than 100 characters."],
                "duration": ["Ensure this value is less than or equal to 2147483647."],
                "host": ["Ensure this field has no more than 100 characters."],
                "participants": ["List contains 11 items, it should contain no more than 10."]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_podcast(self):

        podcast_name = "The Real Python Podcast – Real Python"
        podcast_participants = ["Vishal", "Rahul", "Rohit", "Amogh"]
        podcast_host = "Dan Bader"
        podcast_duration = 214
        now = timezone.now()
        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": PODCAST,
                "audiofilemetadata": {
                    "name": podcast_name,
                    "duration": podcast_duration,
                    "participants": podcast_participants,
                    "host": podcast_host
                }
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, PodcastSerializer(instance=Podcast.objects.get()).data)
        self.assertGreater(parse_datetime(response.data.get('uploaded_time')), now)
        self.assertEqual(Podcast.objects.count(), 1)

    def test_create_audiobook_with_empty_metadata_body(self):

        response = self.client.post(path=self.url, data={"audiofiletype": AUDIOBOOK, "audiofilemetadata": {}})
        self.assertEqual(
            response.data,
            {
                "name": [
                    "This field is required."
                ],
                "duration": [
                    "This field is required."
                ],
                "author": [
                    "This field is required."
                ],
                "narrator": [
                    "This field is required."
                ]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_audiobook_metadata_field_data_type_validation(self):

        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": AUDIOBOOK,
                "audiofilemetadata": {
                    "name": {'k': 'v'},
                    "duration": 12.091283,
                    "author": [123],
                    "narrator": [123]
                }
            }
        )
        self.assertEqual(
            response.data,
            {
                "name": ["Not a valid string."],
                "duration": ["A valid integer is required."],
                "author": ["Not a valid string."],
                "narrator": ["Not a valid string."]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_audiobook_metadata_field_validation(self):

        random_string = "".join(random.choices(f'{string.ascii_uppercase}{string.ascii_lowercase}', k=101))
        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": AUDIOBOOK,
                "audiofilemetadata": {
                    "name": random_string,
                    "duration": 2147483648,
                    "author": random_string,
                    "narrator": random_string
                }
            }
        )
        self.assertEqual(
            response.data,
            {
                "name": ["Ensure this field has no more than 100 characters."],
                "duration": ["Ensure this value is less than or equal to 2147483647."],
                "author": ["Ensure this field has no more than 100 characters."],
                "narrator": ["Ensure this field has no more than 100 characters."]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_audiobook(self):

        audiobook_name = "The Psychology of Money"
        audiobook_author = "Morgan Housel"
        audiobook_narrated_by = "Chris Hill"
        audiobook_duration = 214
        now = timezone.now()
        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": AUDIOBOOK,
                "audiofilemetadata": {
                    "name": audiobook_name,
                    "duration": audiobook_duration,
                    "author": audiobook_author,
                    "narrator": audiobook_narrated_by
                }
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, AudioBookSerializer(instance=AudioBook.objects.get()).data)
        self.assertGreater(parse_datetime(response.data.get('uploaded_time')), now)
        self.assertEqual(AudioBook.objects.count(), 1)


class AudioFileDeleteTests(APITestCase):

    def test_delete_podcast(self):

        podcast = Podcast.objects.create(
            name="The Real Python Podcast – Real Python",
            participants=["Vishal", "Rahul", "Rohit", "Amogh"],
            host="Dan Bader",
            duration=214
        )
        api_url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': PODCAST, 'audiofileid': podcast.id}
        )
        response = self.client.delete(path=api_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Podcast.objects.count(), 0)

    def test_delete_song(self):

        song = Song.objects.create(
            name="Rolex",
            duration=214
        )
        api_url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': SONG, 'audiofileid': song.id}
        )
        response = self.client.delete(path=api_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Song.objects.count(), 0)

    def test_delete_audiobook(self):

        audiobook = AudioBook.objects.create(
            name="The Real Python Podcast – Real Python",
            author="Dan Bader",
            narrator="Dan Bader",
            duration=214
        )
        api_url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': AUDIOBOOK, 'audiofileid': audiobook.id}
        )
        response = self.client.delete(path=api_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AudioBook.objects.count(), 0)


class AudioFileGetTests(APITestCase):

    def setUp(self):

        self.song, self.podcast, self.audiobook = create_audiofile_objects()

    def test_get_song_by_id(self):

        url = reverse('common-actions-audio-file', kwargs={'audiofiletype': SONG, 'audiofileid': self.song.pk})
        response = self.client.get(url)
        self.assertEqual(response.data, SongSerializer(instance=self.song).data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_podcast_by_id(self):

        url = reverse('common-actions-audio-file', kwargs={'audiofiletype': PODCAST, 'audiofileid': self.podcast.pk})
        response = self.client.get(url)
        self.assertEqual(response.data, PodcastSerializer(instance=self.podcast).data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_audiobook_by_id(self):

        url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': AUDIOBOOK, 'audiofileid': self.audiobook.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.data, AudioBookSerializer(instance=self.audiobook).data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_songs(self):

        url = reverse('list-audio-files', kwargs={'audiofiletype': SONG})
        response = self.client.get(url)
        self.assertEqual(response.data, SongSerializer(Song.objects.all(), many=True).data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_podcasts(self):

        url = reverse('list-audio-files', kwargs={'audiofiletype': PODCAST})
        response = self.client.get(url)
        self.assertEqual(response.data, PodcastSerializer(Podcast.objects.all(), many=True).data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_audiobooks(self):

        url = reverse('list-audio-files', kwargs={'audiofiletype': AUDIOBOOK})
        response = self.client.get(url)
        self.assertEqual(response.data, AudioBookSerializer(AudioBook.objects.all(), many=True).data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AudioFileUpdateTests(APITestCase):

    def setUp(self):

        self.song, self.podcast, self.audiobook = create_audiofile_objects()

    def test_song_update_using_patch(self):

        url = reverse('common-actions-audio-file', kwargs={'audiofiletype': SONG, 'audiofileid': self.song.id})
        patch_response = self.client.patch(url, data={'name': 'Changed'})
        self.assertEqual(patch_response.data, SongSerializer(Song.objects.get()).data)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

    def test_audiobook_update_using_patch(self):

        url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': AUDIOBOOK, 'audiofileid': self.audiobook.id}
        )
        patch_response = self.client.patch(url, data={'name': 'Changed'})
        self.assertEqual(patch_response.data, AudioBookSerializer(AudioBook.objects.get()).data)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

    def test_podcast_update_using_patch(self):

        url = reverse('common-actions-audio-file', kwargs={'audiofiletype': PODCAST, 'audiofileid': self.podcast.id})
        patch_response = self.client.patch(url, data={'name': 'Changed'})
        self.assertEqual(patch_response.data, PodcastSerializer(Podcast.objects.get()).data)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

    def test_audio_file_using_put(self):

        for audio_type in [SONG, PODCAST, AUDIOBOOK]:
            url = reverse(
                'common-actions-audio-file',
                kwargs={'audiofiletype': audio_type, 'audiofileid': 1}
            )
            response = self.client.put(url, data={'name': 'Changed'})
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_song_using_put(self):

        url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': SONG, 'audiofileid': self.song.pk}
        )
        response = self.client.put(url, data={'name': 'Changed', 'duration': self.song.duration})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, SongSerializer(instance=Song.objects.get()).data)

    def test_audiobook_using_put(self):

        url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': AUDIOBOOK, 'audiofileid': self.audiobook.pk}
        )
        response = self.client.put(
            path=url,
            data={
                'name': 'Changed',
                'duration': self.audiobook.duration,
                'author': self.audiobook.author,
                'narrator': 'Changed Narrator'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, AudioBookSerializer(instance=AudioBook.objects.get()).data)

    def test_podcast_using_put(self):

        url = reverse(
            'common-actions-audio-file',
            kwargs={'audiofiletype': PODCAST, 'audiofileid': self.podcast.pk}
        )
        response = self.client.put(
            path=url,
            data={
                'name': 'Changed',
                'duration': self.audiobook.duration,
                'host': 'Myself',
                'Participants': []
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, PodcastSerializer(instance=Podcast.objects.get()).data)
