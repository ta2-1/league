#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import make_option

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand, NoArgsCommand

from league.models import League, LeagueCompetitor, Game, Rating
from league.utils import league_get_N, league_get_DELTA


class Command(NoArgsCommand):
    help = "Recalculate league."
    shared_option_list = (
        make_option('--end', action='store_true', dest='is_finished',
                    help='Flag if league is finished'),
    )
    option_list = NoArgsCommand.option_list + shared_option_list

    def handle_noargs(self, **options):
        league_id = 1007
        first_penalty_month = 3
        is_finished = options.get('is_finished', False)
        league = League.objects.get(id=league_id)
        Rating.objects.filter(league=league).delete()
        saved_month = league.start_date.strftime('%Y-%m')
        month_number = 1
        for game in Game.objects.filter(league=league).order_by('end_datetime'):
            month = game.end_datetime.strftime('%Y-%m')
            if month != saved_month:
                month_number += 1
                if month_number > first_penalty_month:
                    call_command('penalize', month=saved_month)
                saved_month = month
            game.save()
            print u"%s" % game
        if is_finished:
            call_command('penalize', '--month=%s' % saved_month)

