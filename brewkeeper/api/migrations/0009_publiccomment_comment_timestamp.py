# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20151113_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='publiccomment',
            name='comment_timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 14, 18, 34, 43, 18025), auto_now=True),
            preserve_default=False,
        ),
    ]
