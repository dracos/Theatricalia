# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enable_comments', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(unique_for_month=b'created')),
                ('title', models.CharField(max_length=100)),
                ('visible', models.BooleanField(default=False)),
                ('body', models.TextField()),
                ('body_html', models.TextField(editable=False, blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT)),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
            },
        ),
    ]
