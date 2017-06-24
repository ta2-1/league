# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-03 08:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0006_remove_league_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='statement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stated_leagues', to='flatpages.FlatPage', verbose_name='\u041f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043b\u0438\u0433\u0438'),
        ),
    ]