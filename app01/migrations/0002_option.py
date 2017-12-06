# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-04 11:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='选项名称')),
                ('score', models.IntegerField(verbose_name='选项对应的分值')),
                ('qs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Question')),
            ],
        ),
    ]
