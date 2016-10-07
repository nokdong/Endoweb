# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-05 17:20
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0022_auto_20161005_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='Bx_result',
            field=models.CharField(default='입력해주세요', max_length=200, verbose_name='조직검사 결과'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_type',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('E', 'EGD'), ('C', 'Colonoscopy'), ('S', 'Sigmoidoscopy')], max_length=20, verbose_name='내시경 종류'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='patient_sex',
            field=models.CharField(choices=[('M', '남자'), ('F', '여자')], default='m', max_length=10, verbose_name='성별'),
        ),
    ]
