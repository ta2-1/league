# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-27 07:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0012_leaguesettings_rating_off_last_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='show_last_days_results',
            field=models.BooleanField(default=False, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0440\u0430\u0441\u0447\u0435\u0442 \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430 \u0437\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u0434\u043d\u0438'),
        ),
    ]
