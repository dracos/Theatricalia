# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('productions', '0001_initial'),
        ('plays', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('places', '0001_initial'),
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='visit',
            unique_together=set([('user', 'production')]),
        ),
        migrations.AddField(
            model_name='production_companies',
            name='production',
            field=models.ForeignKey(to='productions.Production'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production_companies',
            name='productioncompany',
            field=models.ForeignKey(verbose_name=b'company', to='productions.ProductionCompany'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='companies',
            field=models.ManyToManyField(related_name='productions', null=True, through='productions.Production_Companies', to='productions.ProductionCompany', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='parts',
            field=models.ManyToManyField(related_name='productions', through='productions.Part', to='people.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='places',
            field=models.ManyToManyField(related_name='productions', through='productions.Place', to='places.Place', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='play',
            field=models.ForeignKey(related_name='productions', to='plays.Play'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='production',
            name='seen_by',
            field=models.ManyToManyField(related_name='seen', through='productions.Visit', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='place',
            field=models.ForeignKey(related_name='productions_here', to='places.Place'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='production',
            field=models.ForeignKey(to='productions.Production'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='part',
            name='person',
            field=models.ForeignKey(to='people.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='part',
            name='production',
            field=models.ForeignKey(to='productions.Production'),
            preserve_default=True,
        ),
    ]
