from django.db import models
from django.contrib.postgres import fields
from django.core import validators

from core import constants
from audiofile.model_validators import past_validator


class AudioFile(models.Model):

    name = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()
    uploaded_time = models.DateTimeField(validators=[past_validator], auto_now_add=True)

    class Meta:

        abstract = True


class Song(AudioFile):

    class Meta:

        db_table = constants.SONG


class Podcast(AudioFile):

    host = models.CharField(max_length=100)
    participants = fields.ArrayField(base_field=models.CharField(max_length=100), size=10)
    # participants = models.JSONField(validators=[validators.MaxLengthValidator(10)])

    class Meta:

        db_table = constants.PODCAST


class AudioBook(AudioFile):

    author = models.CharField(max_length=100)
    narrator = models.CharField(max_length=100)

    class Meta:

        db_table = constants.AUDIOBOOK
