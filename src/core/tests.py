import string
import random

from rest_framework import status
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from core.models import AudioFile, Song, Podcast


class AudioFileCreateTests(APITestCase):

    def test_create_audio_file_without_data(self):

        url = reverse('create-audio-file')
        response = self.client.post(path=url, data={})
        self.assertEqual(response.data, {"audiofiletype": ["This field is required."]})
        self.assertEqual(response.status_code, 400)


class SongTests(APITestCase):

    url = reverse('create-audio-file')

    def test_create_song_with_wrong_audiotype_choice(self):

        response = self.client.post(path=self.url, data={'audiofiletype': 'somethingrandom'})
        self.assertEqual(response.data, {"audiofiletype": ["\"somethingrandom\" is not a valid choice."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_without_audio_metadata(self):

        response = self.client.post(path=self.url, data={'audiofiletype': 'song'})
        self.assertEqual(response.data, {"audiofilemetadata": ["This field is required"]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_with_empty_metadata_body(self):

        response = self.client.post(path=self.url, data={"audiofiletype": "song", "audiofilemetadata": {}})
        self.assertEqual(response.data, {"name": ["This field is required."], "duration": ["This field is required."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_metadata_field_data_type_validation(self):

        response = self.client.post(
            path=self.url,
            data={
                "audiofiletype": "song",
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
                "audiofiletype": "song",
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
            "audiofiletype": "song",
            "audiofilemetadata": {
                "name": song_name,
                "duration": song_duration
            }
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('name'), song_name)
        self.assertEqual(response.data.get('duration'), song_duration)
        self.assertGreater(parse_datetime(response.data.get('uploaded_time')), now)
        self.assertEqual(Song.objects.count(), 1)
        self.assertEqual(Song.objects.get().name, song_name)
        self.assertEqual(Song.objects.get().duration, song_duration)
