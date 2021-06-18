# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-11-22 10:01
from __future__ import unicode_literals

from django.db import migrations


def update_gcs_to_gcp(apps, schema_editor):
	CloudAssetsData = apps.get_model('redtree_app', 'CloudAssetsData')
	gcs_objs = CloudAssetsData.objects.filter(category="GCS")
	gcs_objs.update(category="GCP")


class Migration(migrations.Migration):

    dependencies = [
        ('redtree_app', '0026_auto_20191122_0453'),
    ]

    operations = [
    	migrations.RunPython(update_gcs_to_gcp),
    ]