# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(help_text='e.g. \u201cRomeo\u201d or \u201cDirector\u201d', max_length=200, verbose_name='R\xf4le', blank=True)),
                ('cast', models.NullBooleanField(help_text='Crew includes all non-cast, from director to musicians to producers', verbose_name=b'Cast/Crew')),
                ('credited_as', models.CharField(help_text='if they were credited differently to their name, or \u201cuncredited\u201d', max_length=100, blank=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('start_date', fields.ApproximateDateField(max_length=10, blank=True)),
                ('end_date', fields.ApproximateDateField(max_length=10, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', fields.ApproximateDateField(max_length=10, blank=True)),
                ('press_date', models.DateField(null=True, blank=True)),
                ('end_date', fields.ApproximateDateField(max_length=10, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Production',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('source', models.TextField(blank=True)),
                ('url', models.URLField(verbose_name=b'Web page', blank=True)),
                ('book_tickets', models.URLField(verbose_name=b'Booking URL', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Production_Companies',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'production-company many-to-many',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductionCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(verbose_name=b'Website', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'production companies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recommend', models.BooleanField()),
                ('date', fields.ApproximateDateField(default=b'', max_length=10, blank=True)),
                ('production', models.ForeignKey(to='productions.Production')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
