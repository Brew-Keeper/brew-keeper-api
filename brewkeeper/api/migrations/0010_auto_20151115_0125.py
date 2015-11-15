# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_publiccomment_comment_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicrating',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='publicrating',
            unique_together=set([('recipe', 'user')]),
        ),
    ]
