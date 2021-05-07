# Generated by Django 3.2.1 on 2021-05-07 13:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_podcast_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='participants',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=10),
        ),
    ]
