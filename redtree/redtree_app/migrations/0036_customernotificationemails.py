# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2020-04-02 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redtree_app', '0035_appliances_port'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerNotificationEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('host_ip', models.CharField(blank=True, max_length=20, null=True)),
                ('last_sent', models.DateTimeField(blank=True, null=True)),
                ('email_success', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Customer Emails List',
            },
        ),
    ]
