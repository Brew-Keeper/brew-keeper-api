# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20151105_1725'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publiccomment',
            old_name='comments',
            new_name='public_comments',
        ),
        migrations.RenameField(
            model_name='publicrating',
            old_name='ratings',
            new_name='public_rating',
        ),
        migrations.AddField(
            model_name='recipe',
            name='average_rating',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
