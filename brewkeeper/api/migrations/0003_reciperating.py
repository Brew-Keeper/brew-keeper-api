# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20151103_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeRating',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('ratings', models.PositiveSmallIntegerField()),
                ('recipe', models.ForeignKey(to='api.Recipe')),
            ],
            options={
                'default_related_name': 'ratings',
            },
        ),
    ]
