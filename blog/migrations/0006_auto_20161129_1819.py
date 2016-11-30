# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-29 18:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_remove_userprofile_profile_picture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='description',
            new_name='body',
        ),
        migrations.RemoveField(
            model_name='post',
            name='downvotes',
        ),
        migrations.RemoveField(
            model_name='post',
            name='upvotes',
        ),
    ]
