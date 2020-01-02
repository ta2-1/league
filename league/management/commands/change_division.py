#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from league.models import League, LeagueCompetitor, LeagueCompetitorLeagueChange


class Command(BaseCommand):
    help = "Move competitors between divisions"

    def add_arguments(self, parser):
        parser.add_argument(
            'league_group_id',
            help='Current league group id'
        )
        super(Command, self).add_arguments(parser)

    def handle(self, **options):
        league_group_id = options.get('league_group_id', None)
        logger = logging.getLogger('rating')

        prev_division = None
        prev_rating = None
        lcc_for_next_divisison = None
        for division in League.objects.filter(group_id=league_group_id).order_by('division'):
            lcc = sorted(
                map(lambda x: {
                    'object': x,
                    'rating': x.rating() },
                    LeagueCompetitor.objects.filter(
                        league=division)), key=lambda x: x['rating'], reverse=True)

            if lcc_for_next_divisison is not None:
                for lc in lcc_for_next_divisison:
                    logger.info(u"%s [%s, %s]" % (lc['object'].competitor.lastName, division.division, lcc[2]['rating']))

                    change = LeagueCompetitorLeagueChange(
                        old_league=prev_division,
                        new_league=division,
                        competitor=lc['object'].competitor,
                        new_rating=lcc[2]['rating'])
                    change.save()

            if prev_division is not None:
                for lc in lcc[:2]:
                    logger.info(u"%s [%s, %s]" % (lc['object'].competitor.lastName, prev_division.division, prev_rating))

                    change = LeagueCompetitorLeagueChange(
                        old_league=division,
                        new_league=prev_division,
                        competitor=lc['object'].competitor,
                        new_rating=prev_rating)
                    change.save()

            lcc_for_next_divisison = lcc[14:]
            prev_division = division
            prev_rating = lcc[13]['rating']
