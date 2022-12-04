# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_userinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicComment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('public_comment', models.TextField()),
            ],
            options={
                'default_related_name': 'public_comments',
            },
        ),
        migrations.CreateModel(
            name='PublicRating',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('public_rating', models.PositiveSmallIntegerField()),
            ],
            options={
                'default_related_name': 'public_ratings',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='average_rating',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='publicrating',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='publicrating',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='publiccomment',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe', on_delete=models.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='publiccomment',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING),
        ),
    ]
