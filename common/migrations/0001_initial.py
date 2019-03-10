# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('productions', '0004_auto_20161227_1833'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('enabled', models.BooleanField(default=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.PROTECT)),
                ('user', models.ForeignKey(related_name='alerts', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='AlertLocal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('enabled', models.BooleanField(default=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('user', models.ForeignKey(related_name='local_alerts', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='AlertSent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alert', models.ForeignKey(to='common.Alert', on_delete=models.CASCADE)),
                ('production', models.ForeignKey(to='productions.Production', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Prelaunch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='alertlocal',
            unique_together=set([('user', 'latitude', 'longitude')]),
        ),
        migrations.AlterUniqueTogether(
            name='alert',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
