# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_reciperating'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('comments', models.TextField()),
                ('recipe', models.ForeignKey(to='api.Recipe')),
            ],
            options={
                'default_related_name': 'comments',
            },
        ),
        migrations.CreateModel(
            name='PublicRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('ratings', models.PositiveSmallIntegerField()),
                ('recipe', models.ForeignKey(to='api.Recipe')),
            ],
            options={
                'default_related_name': 'ratings',
            },
        ),
        migrations.RemoveField(
            model_name='reciperating',
            name='recipe',
        ),
        migrations.DeleteModel(
            name='RecipeRating',
        ),
    ]
