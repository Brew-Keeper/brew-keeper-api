# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0005_auto_20151109_2200'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('reset_string', models.CharField(max_length=27, blank=True, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)),
            ],
        ),
    ]
