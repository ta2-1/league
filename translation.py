from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site

from modeltranslation.translator import translator, TranslationOptions

from rating.models import Tournament, Competitor, Rule, Location, Category
from league.models import (League, LeagueTournament, LeagueTournamentWithSets,
                           LeagueTournamentSet, LeagueSettings)
from partners.models import Partner


class SiteTranslationOptions(TranslationOptions):
    fields = ('name', )
translator.register(Site, SiteTranslationOptions)


class TournamentTranslationOptions(TranslationOptions):
    fields = ('title', )
translator.register(Tournament, TournamentTranslationOptions)

class CategoryTranslationOptions(TranslationOptions):
    fields = ('title', )
translator.register(Category, CategoryTranslationOptions)

class LocationTranslationOptions(TranslationOptions):
    fields = ('title', 'address')
translator.register(Location, LocationTranslationOptions)

class RuleTranslationOptions(TranslationOptions):
    fields = ('text', )
translator.register(Rule, RuleTranslationOptions)

class CompetitorTranslationOptions(TranslationOptions):
    fields = ('firstName', 'lastName', )
translator.register(Competitor, CompetitorTranslationOptions)

class LeagueTranslationOptions(TranslationOptions):
    fields = ('title', )
translator.register(League, LeagueTranslationOptions)
translator.register(LeagueTournament, LeagueTranslationOptions)
translator.register(LeagueTournamentWithSets, LeagueTranslationOptions)

class LeagueTournamentSetTranslationOptions(TranslationOptions):
    fields = ('name', )
translator.register(LeagueTournamentSet, LeagueTournamentSetTranslationOptions)

class LeagueSettingsTranslationOptions(TranslationOptions):
    fields = ('title', )
translator.register(LeagueSettings, LeagueSettingsTranslationOptions)

class FlatPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content', )
translator.register(FlatPage, FlatPageTranslationOptions)
    

class PartnerTranslationOptions(TranslationOptions):
    fields = ('name', 'label', )
translator.register(Partner, PartnerTranslationOptions)
