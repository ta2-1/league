#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.timezone import make_naive

from league.models import League, Game, Rating


class Command(BaseCommand):
    help = "Recalculate league."

    def add_arguments(self, parser):
        parser.add_argument(
            'league_id',
            help='current_league_id'
        )
        parser.add_argument(
            '--end',
            action='store_true',
            dest='is_finished',
            help='Flag if league is finished'
        )
        super(Command, self).add_arguments(parser)

    def handle(self, **options):
        league_id = options.get('league_id', None)
        first_penalty_month = 10 #3
        is_finished = options.get('is_finished', False)
        league = League.objects.get(id=league_id)
        Rating.objects.filter(league=league).delete()
        saved_month = league.start_date.strftime('%Y-%m')
        month_number = 1
        for game in Game.objects.filter(league=league).order_by('end_datetime', 'id'):
            month = make_naive(game.end_datetime).strftime('%Y-%m')
            if month != saved_month:
                debug_condition = True
                month_number += 1
                if month_number > first_penalty_month + 1:
                    if debug_condition:
                        import pdb; pdb.set_trace()
                        call_command('penalize', league_id, month=saved_month)
                saved_month = month
            game.save()
            print u"%s" % game
        if is_finished:
            call_command('penalize', league_id, '--month=%s' % saved_month)
