from django.conf import settings
from django.conf.urls import include, url

import lang_view
from rating import views as rating_views
from league import views as league_views

from django.contrib import admin

from rest_framework import routers

from league.views import GameViewSet, LeagueViewSet, LocationViewSet

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'games', GameViewSet)

urlpatterns = [

    url(r'^$', rating_views.IndexView.as_view(), {}, name="index"),
    url(r'^search/$', rating_views.SearchView.as_view(), {}, name="search"),
    url(r'^tournaments/rating/rules/$', rating_views.RulesView.as_view(), {}, name="rules"),

    url(r'^tournaments/$', rating_views.tournaments, name="tournaments"),
    url(r'^tournaments/list/$', rating_views.tournament_list, name="tournament_list"),
    url(r'^tournaments/(?P<object_id>\d+)/$', rating_views.tournament, name='tournament'),
    url(r'^tournaments/(?P<tournament_id>\d+)/categories/(?P<category_id>[\w\d]+)/$', rating_views.resultset, name='resultset'),

    url(r'^tournaments/rating/$', rating_views.categories),
    url(r'^tournaments/rating/(?P<category_id>\d+)/$', rating_views.RatingView.as_view(), {}, name='category'),

    url(r'^competitors/$', rating_views.competitors, name='competitors'),
    url(r'^competitors/(?P<object_id>\d+)/$', rating_views.CompetitorView.as_view(), {}, name='competitor'),

    url(r'^competitors/(?P<competitor_id>\d+)/leagues/$', league_views.competitor_leagues, name='competitor_leagues'),
    url(r'^competitors/(?P<competitor_id>\d+)/leagues/list/$', league_views.competitor_league_list,{'template_name': 'league/competitor_detail.html'}, name='competitor_league_list'),

    url(r'^competitors/(?P<competitor_id>\d+)/leagues/(?P<league_id>\d+)/$', league_views.competitor,{'template_name': 'league/competitor_detail.html'}, name='competitor_league'),
    url(r'^competitors/(?P<competitor_id>\d+)/rivals/$', league_views.competitor_rivals, {'template_name': 'league/competitor_rivals.html'}, name='competitor_rivals'),

    url(r'^competitors/(?P<competitor1_id>\d+)/vs/(?P<competitor2_id>\d+)/$', league_views.competitors_vs, {'template_name': 'league/competitors_vs.html'}, name='competitors_vs'),

    url(r'^leagues/$', league_views.LeaguesView.as_view(), {}, name='leagues'),
    url(r'^leagues/list/$', league_views.league_list, {'template_name': 'league/object_list.html'}, name='league_list'),
    url(r'^leagues/(?P<league_id>\d+)/$', league_views.LeagueRatingView.as_view(), {}, name='league_rating'),
    url(r'^leagues/(?P<league_id>\d+)/games/$', league_views.LeagueGamesView.as_view(), {}, name='league_games'),
    url(r'^leagues/(?P<league_id>\d+)/results/$', league_views.LeagueResultsView.as_view(), {}, name='league_results'),
    url(r'^leagues/(?P<league_id>\d+)/penalties/$', league_views.LeaguePenaltiesView.as_view(), {}, name='league_penalties'),
    url(r'^leagues/(?P<league_id>\d+)/competitors/(?P<competitor_id>\d+)/gamerivals/$', league_views.competitor_game_rivals, {'template_name': 'league/competitor_game_rivals.html'}, name='competitor_game_rivals'),

    url(r'^leagues/(?P<league_id>\d+)/statement/$', league_views.LeagueStatementView.as_view(), {}, name='league_statement'),
    url(r'^leagues/(?P<league_id>\d+)/rules/$', league_views.LeagueRulesView.as_view(), {}, name='league_rules'),

    url(r'^i18n/setlang/', lang_view.set_language),


    #API not for MENU
    url(r'^leagues/(?P<league_id>\d+)/competitors/(?P<competitor_id>\d+)/opponents/$', league_views.competitor_opponents, name='competitor_opponents'),


    #url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/league/(?P<league_id>\d+)/game/add', league_views.add_game, name='add_game'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^rosetta/', include('rosetta.urls')),
    #url(r'^admin_tools/', include('admin_tools.urls')),

    url(r'^api/v0/', include(router.urls)),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    pass
