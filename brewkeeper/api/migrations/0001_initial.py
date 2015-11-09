# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BrewNote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('body', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-timestamp'],
                'default_related_name': 'brewnotes',
            },
        ),
        migrations.CreateModel(
            name='PublicComment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('public_comment', models.TextField()),
            ],
            options={
                'default_related_name': 'public_comments',
            },
        ),
        migrations.CreateModel(
            name='PublicRating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('public_rating', models.PositiveSmallIntegerField()),
            ],
            options={
                'default_related_name': 'public_ratings',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_brewed_on', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=50)),
                ('orientation', models.CharField(max_length=8, blank=True, null=True)),
                ('rating', models.PositiveSmallIntegerField(default=0)),
                ('general_recipe_comment', models.TextField(blank=True, null=True)),
                ('bean_name', models.CharField(max_length=50, blank=True, null=True)),
                ('roast', models.CharField(max_length=15, blank=True, null=True)),
                ('grind', models.CharField(max_length=30, blank=True, null=True)),
                ('total_bean_amount', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('bean_units', models.CharField(max_length=12, blank=True, null=True)),
                ('water_type', models.CharField(max_length=50, blank=True, null=True)),
                ('total_water_amount', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('water_units', models.CharField(max_length=12, blank=True, null=True)),
                ('temp', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('brew_count', models.PositiveIntegerField(default=0)),
                ('total_duration', models.PositiveSmallIntegerField(default=0)),
                ('average_rating', models.FloatField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-rating'],
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('step_number', models.PositiveSmallIntegerField()),
                ('step_title', models.CharField(max_length=50)),
                ('step_body', models.CharField(max_length=255, blank=True, null=True)),
                ('duration', models.PositiveSmallIntegerField(default=0)),
                ('water_amount', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('water_units', models.CharField(max_length=12, blank=True, null=True)),
                ('recipe', models.ForeignKey(to='api.Recipe')),
            ],
            options={
                'ordering': ['step_number'],
                'default_related_name': 'steps',
            },
        ),
        migrations.AddField(
            model_name='publicrating',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe'),
        ),
        migrations.AddField(
            model_name='publicrating',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publiccomment',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe'),
        ),
        migrations.AddField(
            model_name='publiccomment',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='brewnote',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe'),
        ),
    ]
