# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fields


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('town', models.CharField(max_length=50, blank=True)),
                ('postcode', models.CharField(max_length=10, blank=True)),
                ('telephone', models.CharField(max_length=50, blank=True)),
                ('type', models.CharField(blank=True, max_length=100, choices=[(b'proscenium', b'Proscenium Arch'), (b'thrust', b'Thrust'), (b'multiple', b'Multiple'), (b'other', b'Other')])),
                ('size', models.CharField(max_length=100, verbose_name=b'Seats', blank=True)),
                ('opening_date', fields.ApproximateDateField(max_length=10, blank=True)),
                ('closing_date', fields.ApproximateDateField(default=b'', max_length=10, blank=True)),
                ('url', models.URLField(verbose_name=b'URL', blank=True)),
                ('wikipedia', models.URLField(blank=True)),
                ('country', models.ForeignKey(blank=True, to='countries.Country', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
