# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-06 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0028_auto_20161006_0248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='follow_up',
            field=models.IntegerField(default=0, verbose_name='추적검사 기간'),
        ),
    ]
