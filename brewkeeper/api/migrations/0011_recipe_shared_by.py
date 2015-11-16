# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20151115_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='shared_by',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
