import string
import random

from rest_framework import status
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from core.constants import PODCAST, SONG, AUDIOBOOK
from core.models import AudioFile, Song, Podcast


class AudioFileCreateTests(APITestCase):

    url = reverse('create-audio-file')

    def test_create_audio_file_without_data(self):

        response = self.client.post(path=self.url, data={})
        self.assertEqual(response.data, {"audiofiletype": ["This field is required."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_with_wrong_audiotype_choice(self):

        response = self.client.post(path=self.url, data={'audiofiletype': 'somethingrandom'})
        self.assertEqual(response.data, {"audiofiletype": ["\"somethingrandom\" is not a valid choice."]})
        self.assertEqual(response.status_code, 400)

    def test_create_song_without_audio_metadata(self):

        response = self.client.post(path=self.url, data={'audiofiletype': random.choice([AUDIOBOOK, SONG, PODCAST])})
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
        self.assertEqual(response.data.get('name'), song_name)
        self.assertEqual(response.data.get('duration'), song_duration)
        self.assertGreater(parse_datetime(response.data.get('uploaded_time')), now)
        self.assertEqual(Song.objects.count(), 1)
        self.assertEqual(Song.objects.get().name, song_name)
        self.assertEqual(Song.objects.get().duration, song_duration)

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
        self.assertEqual(response.data.get('name'), podcast_name)
        self.assertEqual(response.data.get('host'), podcast_host)
        self.assertEqual(response.data.get('participants'), podcast_participants)
        self.assertGreater(parse_datetime(response.data.get('uploaded_time')), now)
        self.assertEqual(Podcast.objects.count(), 1)
        self.assertEqual(Podcast.objects.get().name, podcast_name)
        self.assertEqual(Podcast.objects.get().duration, podcast_duration)
        self.assertEqual(Podcast.objects.get().participants, podcast_participants)

