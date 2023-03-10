# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-09-29 22:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0001_initial'),
        ('league', '0020_auto_20190930_0057'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueCompetitorLeagueChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_rating', models.FloatField(verbose_name='\u0420\u0435\u0439\u0442\u0438\u043d\u0433 \u0432 \u043d\u043e\u0432\u043e\u0439 \u043b\u0438\u0433\u0435')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('competitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating.Competitor', verbose_name='\u0423\u0447\u0430\u0441\u0442\u043d\u0438\u043a')),
                ('new_league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='new_league_changes', to='league.League', verbose_name='\u041b\u0438\u0433\u0430 (\u043d\u043e\u0432\u0430\u044f)')),
                ('old_league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_league_changes', to='league.League', verbose_name='\u041b\u0438\u0433\u0430 (\u0441\u0442\u0430\u0440\u0430\u044f)')),
            ],
        ),
    ]
