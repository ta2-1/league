# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-27 07:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0013_league_show_last_days_results'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguecompetitor',
            name='tournament_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='league.LeagueTournamentSet', verbose_name='\u041a\u0430\u0442\u0435\u0440\u043e\u0440\u0438\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430'),
        ),
    ]
