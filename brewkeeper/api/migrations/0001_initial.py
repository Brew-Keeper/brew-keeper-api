# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brewnote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('body', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_brewed_on', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=50)),
                ('orientation', models.CharField(null=True, max_length=8, blank=True)),
                ('rating', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('general_recipe_comment', models.TextField(null=True, blank=True)),
                ('bean_name', models.CharField(null=True, max_length=50, blank=True)),
                ('roast', models.CharField(null=True, max_length=15, blank=True)),
                ('grind', models.CharField(null=True, max_length=30, blank=True)),
                ('total_bean_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('bean_units', models.CharField(null=True, max_length=12, blank=True)),
                ('water_type', models.CharField(null=True, max_length=50, blank=True)),
                ('total_water_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('water_units', models.CharField(null=True, max_length=12, blank=True)),
                ('temp', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('brew_count', models.PositiveIntegerField(default=0)),
                ('total_duration', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['-rating'],
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('step_number', models.PositiveSmallIntegerField()),
                ('step_title', models.CharField(max_length=50)),
                ('step_detail', models.CharField(null=True, max_length=255, blank=True)),
                ('duration', models.PositiveSmallIntegerField(default=0)),
                ('water_amount', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('recipe', models.ForeignKey(to='api.Recipe')),
            ],
        ),
        migrations.AddField(
            model_name='brewnote',
            name='recipe',
            field=models.ForeignKey(to='api.Recipe'),
        ),
    ]
