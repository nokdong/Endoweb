# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-03 17:33
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0015_auto_20161004_0158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='exam_Bx',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Bx', 'Bx'), ('CLO', 'CLO'), ('Polypectomy', 'Polypectomy'), ('EMR', 'EMR'), ('ForeignBody', 'Foreign Body Remove'), ('BleedingControl', 'Bleeding Control')], max_length=20, verbose_name='시술'),
        ),
    ]
