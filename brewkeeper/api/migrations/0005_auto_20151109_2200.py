# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20151108_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='total_bean_amount',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
