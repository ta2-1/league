#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

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

        now = timezone.now()
        dt = now - relativedelta(months=1)
        r_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for lc in lcc:
            #print "----"
            #print lc
            new_rivals_count = lc.rival_count_in_month(dt)
            if new_rivals_count < 4:
                penalty = -2.5*(4 - new_rivals_count)

                penalty_count = Rating.objects.filter(
                    type='penalty', datetime=dt, player=lc.competitor).count()
                if penalty_count == 0:
                    rating = lc.rating(now)
                    r = Rating(league=lc.league, type='penalty', datetime=r_dt, player=lc.competitor,
                               delta=penalty, rating_before=rating)
                    print r
                    r.save()
