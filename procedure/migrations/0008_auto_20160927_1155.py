# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-27 02:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0007_auto_20160926_0241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='exam_date',
            field=models.DateField(auto_now_add=True, verbose_name='검사 날짜'),
        ),
    ]
