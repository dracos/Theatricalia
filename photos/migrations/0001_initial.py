# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sorl.thumbnail.fields
import photos.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_visible', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('photo', sorl.thumbnail.fields.ImageField(upload_to=photos.models.get_upload_to, max_length=255, verbose_name='Photograph')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.PROTECT)),
            ],
        ),
    ]
