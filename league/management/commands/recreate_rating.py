#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.core.management.base import BaseCommand

from league.models import League, Game, Rating


class Command(BaseCommand):
    help = "Recalculate league."

    def add_arguments(self, parser):
        parser.add_argument(
            '--end',
            action='store_true',
            dest='is_finished',
            help='Flag if league is finished'
        )
        super(Command, self).add_arguments(parser)

    def handle(self, **options):
        league_id = 1010
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

