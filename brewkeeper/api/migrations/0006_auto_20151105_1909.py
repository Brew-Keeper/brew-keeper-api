# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20151105_1843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publiccomment',
            old_name='public_comments',
            new_name='public_comment',
        ),
    ]
