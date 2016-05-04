#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import make_option
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand, NoArgsCommand

from league.models import get_current_league, League, LeagueCompetitor, Rating

class Command(BaseCommand):
    help = "Penalize competitors who does not play much."
    shared_option_list = (
        make_option('--month', dest='month', help='past month for penalties'),
    )

    option_list = BaseCommand.option_list + shared_option_list
    current_league_id = 1007

    def handle(self, *args, **options):
        l = League.objects.get(id=self.current_league_id)
        lcc = LeagueCompetitor.objects.filter(league=l)

        league_dt = datetime.combine(l.start_date, time()) \
                            .replace(hour=0, minute=0, second=0)

        month = options.get('month', None)
        if month is not None:
            start_dt = datetime.strptime(month, '%Y-%m').replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            dt = start_dt + relativedelta(months=1)
            end_dt = dt - timedelta(seconds=1)
        else:
            dt = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_dt = dt - relativedelta(months=1)
            end_dt = dt - timedelta(seconds=1)

        for lc in lcc:
            #print "----"
            #print lc
            old_games = set(lc.rivals(league_dt, start_dt))
            new_games = set(lc.rivals(start_dt, end_dt))
            #print old_games
            #print new_games
            new_rivals_count = len(new_games - old_games)
            total_rivals_count = len(new_games | old_games)
            if total_rivals_count < 10:
                if new_rivals_count == 0:
                    penalty = -10
                elif new_rivals_count == 1:
                    penalty = -5
                else:
                    penalty = 0
            else:
                if len(new_games) == 0:
                    penalty = -10
                elif len(new_games) == 1:
                    penalty = -5
                else:
                    penalty = 0

            if penalty < 0 and Rating.objects.filter(type='penalty', datetime=dt, player=lc.competitor).count() == 0:
                r = Rating(league=l, type='penalty', datetime=dt, player=lc.competitor,
                           delta=penalty, rating_before=lc.saved_rating(datetime=end_dt))
                print r
                r.save()

