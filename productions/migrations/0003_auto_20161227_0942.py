# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productions', '0002_auto_20161227_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='recommend',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
