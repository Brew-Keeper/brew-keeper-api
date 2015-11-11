# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_recipe_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='water_units',
            field=models.CharField(blank=True, null=True, max_length=12),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='rating',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
