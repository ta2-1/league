# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-30 20:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0001_initial'),
        ('league', '0003_game_added_via_api'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueTournamentResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=10, verbose_name='\u041c\u0435\u0441\u0442\u043e')),
            ],
            options={
                'verbose_name': '\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442',
                'verbose_name_plural': '\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='LeagueTournamentSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('number', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u043e\u0432')),
                ('datetime', models.DateTimeField(blank=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430')),
                ('is_filled', models.BooleanField(default=False, verbose_name='\u0414\u0430\u043d\u043d\u044b\u0435 \u0432\u0432\u0435\u0434\u0435\u043d\u044b \u043f\u043e\u043b\u043d\u043e\u0441\u0442\u044c\u044e')),
            ],
            options={
                'verbose_name': '\u041a\u0430\u0442\u0435\u0440\u043e\u0440\u0438\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430',
                'verbose_name_plural': '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u0442\u0443\u0440\u043d\u0438\u0440\u0430',
            },
        ),
        migrations.AddField(
            model_name='leaguetournamentset',
            name='competitors',
            field=models.ManyToManyField(related_name='resultsets', through='league.LeagueTournamentResult', to='league.LeagueCompetitor'),
        ),
        migrations.AddField(
            model_name='leaguetournamentset',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.League', verbose_name='\u041b\u0438\u0433\u0430'),
        ),
        migrations.AddField(
            model_name='leaguetournamentset',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rating.Location', verbose_name='\u041c\u0435\u0441\u0442\u043e \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430'),
        ),
        migrations.AddField(
            model_name='leaguetournamentresult',
            name='competitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.LeagueCompetitor', verbose_name='\u0423\u0447\u0430\u0441\u0442\u043d\u0438\u043a'),
        ),
        migrations.AddField(
            model_name='leaguetournamentresult',
            name='tournament_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.LeagueTournamentSet', verbose_name='\u0421\u0435\u0442\u043a\u0430 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u043e\u0432'),
        ),
    ]