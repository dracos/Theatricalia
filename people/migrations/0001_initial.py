# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50, verbose_name='Forenames', blank=True)),
                ('last_name', models.CharField(max_length=50)),
                ('first_name_metaphone', models.CharField(max_length=50, editable=False)),
                ('first_name_metaphone_alt', models.CharField(max_length=50, editable=False)),
                ('last_name_metaphone', models.CharField(max_length=50, editable=False)),
                ('last_name_metaphone_alt', models.CharField(max_length=50, editable=False)),
                ('slug', models.SlugField(max_length=100)),
                ('bio', models.TextField(verbose_name='Biography', blank=True)),
                ('dob', fields.ApproximateDateField(max_length=10, verbose_name='Date of birth', blank=True)),
                ('died', fields.ApproximateDateField(max_length=10, verbose_name='Date of death', blank=True)),
                ('imdb', models.URLField(verbose_name='IMDb URL', blank=True)),
                ('musicbrainz', models.URLField(default='', verbose_name='MusicBrainz URL', blank=True)),
                ('wikipedia', models.URLField(verbose_name='Wikipedia URL', blank=True)),
                ('openplaques', models.URLField(default='', verbose_name='OpenPlaques URL', blank=True)),
                ('web', models.URLField(verbose_name='Personal website', blank=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
                'verbose_name_plural': 'people',
            },
            bases=(models.Model,),
        ),
    ]
