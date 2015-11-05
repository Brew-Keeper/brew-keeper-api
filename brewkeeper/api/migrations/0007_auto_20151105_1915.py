# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20151105_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='average_rating',
            field=models.FloatField(default=0),
        ),
    ]
