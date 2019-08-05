#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from league.models import Game


class Command(BaseCommand):
    help = "Calculate rating for last games without rating."

    def add_arguments(self, parser):
        parser.add_argument(
            'league_group_id',
            help='Current league group id'
        )
        super(Command, self).add_arguments(parser)

    def handle(self, **options):
        league_group_id = options.get('league_group_id', None)
        for game in Game.objects.filter(
                league__group_id=league_group_id,
                rating__isnull=True).order_by('end_datetime', 'id'):
            game.save(update_rating=True)
            print u"%s" % game
