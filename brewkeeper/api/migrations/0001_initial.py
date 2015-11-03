# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BrewNote',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('body', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_brewed_on', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=50)),
                ('orientation', models.CharField(null=True, blank=True, max_length=8)),
                ('rating', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('general_recipe_comment', models.TextField(null=True, blank=True)),
                ('bean_name', models.CharField(null=True, blank=True, max_length=50)),
                ('roast', models.CharField(null=True, blank=True, max_length=15)),
                ('grind', models.CharField(null=True, blank=True, max_length=30)),
                ('total_bean_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bean_units', models.CharField(null=True, blank=True, max_length=12)),
                ('water_type', models.CharField(null=True, blank=True, max_length=50)),
                ('total_water_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('water_units', models.CharField(null=True, blank=True, max_length=12)),
                ('temp', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('brew_count', models.PositiveIntegerField(default=0)),
                ('total_duration', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['-rating'],
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('step_number', models.PositiveSmallIntegerField()),
                ('step_title', models.CharField(max_length=50)),
                ('step_detail', models.CharField(null=True, blank=True, max_length=255)),
                ('duration', models.PositiveSmallIntegerField(default=0)),
                ('water_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('recipe', models.ForeignKey(to='api.Recipe')),
            ],
            options={
                'ordering': ['step_number'],
            },
        ),
        migrations.AddField(
            model_name='brewnote',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe'),
        ),
    ]
