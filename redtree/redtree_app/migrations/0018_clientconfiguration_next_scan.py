# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-11-04 10:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redtree_app', '0017_nessusfile_error_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientconfiguration',
            name='next_scan',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
