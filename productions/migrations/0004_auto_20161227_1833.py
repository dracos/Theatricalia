# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productions', '0003_auto_20161227_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='production',
            name='companies',
            field=models.ManyToManyField(related_name='productions', through='productions.Production_Companies', to='productions.ProductionCompany', blank=True),
        ),
    ]
