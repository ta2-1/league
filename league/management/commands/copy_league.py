#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand, NoArgsCommand

from livesettings import config_value

from league.models import get_current_league, League, LeagueCompetitor, Game 

class Command(NoArgsCommand):
    help = "Copy league."

    def handle_noargs(self, **options):
        source_id = 6  
        dest_id = 1004 

        source = League.objects.get(id=source_id)
        dest = League.objects.get(id=dest_id)
        
        lcc = LeagueCompetitor.objects.filter(league=source)
        for lc in lcc:
            lc.pk = None
            lc.league = dest
            lc.save()

        for game in Game.objects.filter(league=source).order_by('end_datetime'):
            game.pk = None
            game.no_record = False
            game.league = dest
            game.save()

