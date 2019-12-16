#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from league.models import Game, LeagueCompetitor


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
        logger = logging.getLogger('rating')

        for game in Game.objects.filter(
                league__group_id=league_group_id,
                rating__isnull=True).order_by('end_datetime', 'id'):
            lc1 = LeagueCompetitor.objects.get(league=game.league, competitor=game.player1)
            lc2 = LeagueCompetitor.objects.get(league=game.league, competitor=game.player2)

            logger.info(u"%s\n\t\tСоперники: %s, %s" % (
                game, lc1.rival_count_in_month(game.start_datetime), lc2.rival_count_in_month(game.start_datetime)))

            game.save(update_rating=True)
