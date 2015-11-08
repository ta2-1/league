#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand, NoArgsCommand

from league.models import League, LeagueCompetitor, Game, Rating 
from league.utils import league_get_N, league_get_DELTA 


class Command(NoArgsCommand):
    help = "Recalculate league."

    def handle_noargs(self, **options):
        league_id = 1005  

        league = League.objects.get(id=league_id)
        
        for game in Game.objects.filter(league=league).order_by('end_datetime'):
            lc1 = LeagueCompetitor.objects.get(league=league, competitor=game.player1)
            lc2 = LeagueCompetitor.objects.get(league=league, competitor=game.player2)
            rating1 = Rating.objects.get(league=league, game=game, player=game.player1)
            rating2 = Rating.objects.get(league=league, game=game, player=game.player2)            
            n = league_get_N(league.settings, game.result1, game.result2)
            min_rival_count = min(lc1.rival_count(game.start_datetime), lc2.rival_count(game.start_datetime))
            r1 = lc1.rating(game.end_datetime)
            r2 = lc2.rating(game.end_datetime)
            delta = league_get_DELTA(league.settings, rating1.rating_before, rating2.rating_before, n, min_rival_count)
            Rating.objects.filter(id=rating1.id).update(delta=delta, rating_after=r1+delta, rating_before=r1)
            Rating.objects.filter(id=rating2.id).update(delta=0-delta, rating_after=r2-delta, rating_before=r2)
            print u"%s" % game

