# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-06-12 07:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redtree_app', '0042_remove_applications_burp_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='screenshot_title',
            field=models.BooleanField(default=False),
        ),
    ]
