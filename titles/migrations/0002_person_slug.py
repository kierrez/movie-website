# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='slug',
            field=models.SlugField(default='', max_length=350),
            preserve_default=False,
        ),
    ]
