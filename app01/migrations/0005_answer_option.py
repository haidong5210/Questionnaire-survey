# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 08:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_auto_20171206_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.Option'),
        ),
    ]
