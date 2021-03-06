# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-22 16:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='patient_age',
        ),
        migrations.AddField(
            model_name='exam',
            name='exam_class',
            field=models.CharField(choices=[('national', 'National'), ('hospital', 'Hospital')], default='hospital', max_length=30, verbose_name='건진/진료'),
        ),
        migrations.AddField(
            model_name='exam',
            name='patient_birth',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='생일'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exam',
            name='Bx_result',
            field=models.CharField(max_length=200, verbose_name='조직검사 결과'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_Bx',
            field=models.CharField(choices=[('y', 'Yes'), ('n', 'No')], default='n', max_length=10, verbose_name='조직검사 유무'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_Dx',
            field=models.CharField(max_length=200, verbose_name='내시경 진단명'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_date',
            field=models.DateField(auto_now_add=True, verbose_name='검사 날짜'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_doc',
            field=models.CharField(choices=[('lyj', 'Lee'), ('ksi', 'Kim')], default='ksi', max_length=30, verbose_name='의사'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_type',
            field=models.CharField(choices=[('upper', 'EGD'), ('lower', 'Colonoscopy')], default='upper', max_length=10, verbose_name='위/대장내시경'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='follow_up',
            field=models.IntegerField(verbose_name='추적검사 기간'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='hospital_no',
            field=models.IntegerField(verbose_name='환자등록 번호'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='patient_name',
            field=models.CharField(max_length=50, verbose_name='환자 이름'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='patient_sex',
            field=models.CharField(choices=[('m', 'male'), ('f', 'female')], default='m', max_length=10, verbose_name='성별'),
        ),
    ]
