# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(verbose_name=b'URL', blank=True)),
                ('wikipedia', models.URLField(blank=True)),
                ('authors', models.ManyToManyField(related_name='plays', to='people.Person', blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='plays.Play', null=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
