# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_datetime', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430', blank=True)),
                ('end_datetime', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f')),
                ('result1', models.SmallIntegerField(verbose_name='\u0421\u0447\u0451\u0442')),
                ('result2', models.SmallIntegerField(verbose_name=' ')),
                ('no_record', models.BooleanField(default=False, verbose_name='\u041d\u0435\u0437\u0430\u0447\u0435\u0442\u043d\u0430\u044f \u0438\u0433\u0440\u0430')),
            ],
            options={
                'verbose_name': '\u0418\u0433\u0440\u0430',
                'verbose_name_plural': '\u0418\u0433\u0440\u044b',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('title_ru', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('title_en', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('start_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430')),
                ('end_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f')),
                ('tournament_a_datetime', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430 (A)', blank=True)),
                ('tournament_b_datetime', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430 (B)', blank=True)),
                ('is_tournament_data_filled', models.BooleanField(default=False, verbose_name='\u0414\u0430\u043d\u043d\u044b\u0435 \u0432\u0432\u0435\u0434\u0435\u043d\u044b \u043f\u043e\u043b\u043d\u043e\u0441\u0442\u044c\u044e')),
                ('visible', models.BooleanField(default=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
            ],
            options={
                'verbose_name': '\u041b\u0438\u0433\u0430',
                'verbose_name_plural': '\u041b\u0438\u0433\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeagueCompetitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paid', models.NullBooleanField(verbose_name='\u041e\u043f\u043b\u0430\u0442\u0438\u043b')),
                ('status', models.CharField(max_length=255, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', blank=True)),
                ('tournament_place', models.CharField(max_length=255, verbose_name='\u041c\u0435\u0441\u0442\u043e', blank=True)),
                ('is_participant', models.BooleanField(default=False, verbose_name='\u041f\u0440\u0438\u043d\u0438\u043c\u0430\u043b \u0443\u0447\u0430\u0441\u0442\u0438\u0435 \u0432 \u0442\u0443\u0440\u043d\u0438\u0440\u0435')),
                ('tournament_category', models.CharField(blank=True, max_length=4, null=True, verbose_name='\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430', choices=[(b'A', '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0410'), (b'B', '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0412')])),
                ('competitor', models.ForeignKey(verbose_name='\u0423\u0447\u0430\u0441\u0442\u043d\u0438\u043a', to='rating.Competitor')),
                ('league', models.ForeignKey(verbose_name='\u041b\u0438\u0433\u0430', to='league.League')),
            ],
            options={
                'verbose_name': '\u0423\u0447\u0430\u0441\u0442\u043d\u0438\u043a \u043b\u0438\u0433\u0438',
                'verbose_name_plural': '\u0423\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u0438 \u043b\u0438\u0433\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeagueSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('title_ru', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('title_en', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('soften_coef', models.PositiveIntegerField(default=20, verbose_name='\u0421\u043c\u044f\u0433\u0447\u0430\u044e\u0449\u0438\u0439 \u043a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442')),
                ('position_difference', models.PositiveIntegerField(default=10, verbose_name='\u0414\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u0430\u044f \u0440\u0430\u0437\u043d\u0438\u0446\u0430 \u0432 \u0437\u0430\u043d\u0438\u043c\u0430\u0435\u043c\u044b\u0445 \u043f\u043e\u0437\u0438\u0446\u0438\u044f\u0445')),
                ('initial_rating', models.PositiveIntegerField(default=100, verbose_name='\u041d\u0430\u0447\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433')),
                ('reliability_rival_quantity', models.PositiveIntegerField(default=4, verbose_name='\u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0441\u043e\u043f\u0435\u0440\u043d\u0438\u043a\u043e\u0432 \u0434\u043b\u044f \u043f\u0440\u0438\u0441\u0432\u043e\u0435\u043d\u0438\u044f \u043c\u0435\u0441\u0442\u0430')),
                ('final_rival_quantity', models.PositiveIntegerField(default=10, verbose_name='\u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0441\u043e\u043f\u0435\u0440\u043d\u0438\u043a\u043e\u0432 \u0434\u043b\u044f \u043f\u0440\u0438\u0441\u0432\u043e\u0435\u043d\u0438\u044f \u0438\u0442\u043e\u0433\u043e\u0432\u043e\u0433\u043e \u043c\u0435\u0441\u0442\u0430')),
                ('n_formula', models.CharField(default=b'result1 - result2', max_length=255, verbose_name='\u0424\u043e\u0440\u043c\u0443\u043b\u0430 N')),
                ('delta_formula', models.CharField(default=b'N + (r2-r1)/SOFTEN_COEF', max_length=255, verbose_name='\u0424\u043e\u0440\u043c\u0443\u043b\u0430 DELTA')),
            ],
            options={
                'verbose_name': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043b\u0438\u0433\u0438',
                'verbose_name_plural': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043b\u0438\u0433\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=25, verbose_name='\u041f\u0440\u0438\u0447\u0438\u043d\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430', choices=[(b'game', '\u0418\u0433\u0440\u0430'), (b'penalty', '\u0428\u0442\u0440\u0430\u0444'), (b'other', '\u0414\u0440\u0443\u0433\u043e\u0435')])),
                ('datetime', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430')),
                ('comment', models.TextField(verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439')),
                ('delta', models.FloatField(verbose_name='\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435')),
                ('rating_before', models.FloatField(verbose_name='\u0420\u0435\u0439\u0442\u0438\u043d\u0433 "\u0414\u043e"')),
                ('rating_after', models.FloatField(verbose_name='\u0420\u0435\u0439\u0442\u0438\u043d\u0433 "\u041f\u043e\u0441\u043b\u0435"')),
                ('game', models.ForeignKey(verbose_name='\u0418\u0433\u0440\u0430', blank=True, to='league.Game', null=True)),
                ('league', models.ForeignKey(verbose_name='\u041b\u0438\u0433\u0430', to='league.League')),
                ('player', models.ForeignKey(verbose_name='\u0418\u0433\u0440\u043e\u043a', to='rating.Competitor')),
            ],
            options={
                'verbose_name': '\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430',
                'verbose_name_plural': '\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='league',
            name='competitors',
            field=models.ManyToManyField(related_name=b'leagues', through='league.LeagueCompetitor', to='rating.Competitor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='league',
            name='location',
            field=models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f \u0442\u0443\u0440\u043d\u0438\u0440\u0430', blank=True, to='rating.Location', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='league',
            name='settings',
            field=models.ForeignKey(verbose_name='\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043b\u0438\u0433\u0438', to='league.LeagueSettings'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='game',
            name='league',
            field=models.ForeignKey(verbose_name='\u041b\u0438\u0433\u0430', to='league.League'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='game',
            name='location',
            field=models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f', to='rating.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='game',
            name='player1',
            field=models.ForeignKey(related_name=b'home_game_set', verbose_name='\u0418\u0433\u0440\u043e\u043a1', to='rating.Competitor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='game',
            name='player2',
            field=models.ForeignKey(related_name=b'guest_game_set', verbose_name='\u0418\u0433\u0440\u043e\u043a2', to='rating.Competitor'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='LeagueAlterTournament',
            fields=[
            ],
            options={
                'verbose_name': '\u0418\u0442\u043e\u0433\u043e\u0432\u044b\u0439 \u0442\u0443\u0440\u043d\u0438\u0440 \u041b\u0438\u0433\u0438 (2)',
                'proxy': True,
                'verbose_name_plural': '\u0418\u0442\u043e\u0433\u043e\u0432\u044b\u0435 \u0442\u0443\u0440\u043d\u0438\u0440\u044b \u041b\u0438\u0433\u0438 (2)',
            },
            bases=('league.league',),
        ),
        migrations.CreateModel(
            name='LeagueTournament',
            fields=[
            ],
            options={
                'verbose_name': '\u0418\u0442\u043e\u0433\u043e\u0432\u044b\u0439 \u0442\u0443\u0440\u043d\u0438\u0440 \u041b\u0438\u0433\u0438',
                'proxy': True,
                'verbose_name_plural': '\u0418\u0442\u043e\u0433\u043e\u0432\u044b\u0435 \u0442\u0443\u0440\u043d\u0438\u0440\u044b \u041b\u0438\u0433\u0438',
            },
            bases=('league.league',),
        ),
    ]
