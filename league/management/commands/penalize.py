#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand

from django_rq import job

from league.models import League, LeagueCompetitor, Rating


class Command(BaseCommand):
    help = "Penalize competitors who does not play much."

    def add_arguments(self, parser):
        parser.add_argument(
            'league_id',
            help='league_id'
        )
        parser.add_argument(
            '--month',
            dest='month',
            help='past month for penalties'
        )
        super(Command, self).add_arguments(parser)


    def handle(self, *args, **options):
        league_id = options.get('league_id', None)
        l = League.objects.get(id=league_id)
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

            penalty_count = Rating.objects.filter(
                type='penalty', datetime=dt, player=lc.competitor).count()
            if penalty < 0 and penalty_count == 0:
                save_rating.delay(lc, penalty, dt, end_dt)


@job
def save_rating(league_competitor, penalty, dt, end_dt):
    competitor = league_competitor.competitor
    league = league_competitor.league
    saved_rating = league_competitor.saved_rating(datetime=end_dt)
    r = Rating(league=league, type='penalty', datetime=dt, player=competitor,
               delta=penalty, rating_before=saved_rating)
    print r
    r.save()
