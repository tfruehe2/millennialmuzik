# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-04 21:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20161129_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicRecommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(max_length=100)),
                ('song_name', models.CharField(max_length=100)),
                ('url', models.URLField(blank=True)),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('what', models.CharField(max_length=144)),
                ('how', models.TextField(blank=True, max_length=250)),
            ],
        ),
    ]