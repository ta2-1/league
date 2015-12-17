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
        league_id = 1007

        league = League.objects.get(id=league_id)
        Rating.objects.filter(league=league).delete()
        for game in Game.objects.filter(league=league).order_by('end_datetime'):
            game.save()
            print u"%s" % game

