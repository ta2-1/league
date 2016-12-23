from django.conf import settings
from django.conf.urls import patterns, include, url

import lang_view

from django.contrib import admin

from rest_framework import routers

from league.views import GameViewSet, LeagueViewSet, LocationViewSet

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'games', GameViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'squash.views.home', name='home'),
    # url(r'^squash/', include('squash.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH,'static')}),

    url(r'^$', 'rating.views.index', {'template_name': 'index.html'}, name="index"),
    url(r'^search/$', 'rating.views.search', {'template_name': 'search.html'}),
    url(r'^tournaments/rating/rules/$', 'rating.views.rules', {'template_name': 'rules.html'}, name="rules"),

    url(r'^tournaments/$', 'rating.views.tournaments', name="tournaments"),
    url(r'^tournaments/list/$', 'rating.views.tournament_list', name="tournament_list"),
    url(r'^tournaments/(?P<object_id>\d+)/$', 'rating.views.tournament', name='tournament'),
    url(r'^tournaments/(?P<tournament_id>\d+)/categories/(?P<category_id>[\w\d]+)/$', 'rating.views.resultset', name='resultset'),

    url(r'^tournaments/rating/$', 'rating.views.categories'),
    url(r'^tournaments/rating/(?P<category_id>\d+)/$', 'rating.views.rating', {'template_name': 'rating/rating_by_category.html'}, name='category'),

    url(r'^competitors/$', 'rating.views.competitors', name='competitors'),
    url(r'^competitors/(?P<object_id>\d+)/$', 'rating.views.competitor',{'template_name': 'rating/competitor_detail.html'}, name='competitor'),

    url(r'^competitors/(?P<competitor_id>\d+)/leagues/$', 'league.views.competitor_leagues', name='competitor_leagues'),
    url(r'^competitors/(?P<competitor_id>\d+)/leagues/list/$', 'league.views.competitor_league_list',{'template_name': 'league/competitor_detail.html'}, name='competitor_league_list'),

    url(r'^competitors/(?P<competitor_id>\d+)/leagues/(?P<league_id>\d+)/$', 'league.views.competitor',{'template_name': 'league/competitor_detail.html'}, name='competitor_league'),
    url(r'^competitors/(?P<competitor_id>\d+)/rivals/$', 'league.views.competitor_rivals',{'template_name': 'league/competitor_rivals.html'}, name='competitor_rivals'),

    url(r'^competitors/(?P<competitor1_id>\d+)/vs/(?P<competitor2_id>\d+)/$', 'league.views.competitors_vs',{'template_name': 'league/competitors_vs.html'}, name='competitors_vs'),

    url(r'^leagues/$', 'league.views.leagues', {'template_name': 'league/current_leagues.html'}, name='leagues'),
    url(r'^leagues/list/$', 'league.views.league_list', {'template_name': 'league/object_list.html'}, name='league_list'),
    url(r'^leagues/(?P<league_id>\d+)/$', 'league.views.league_rating', {'template_name': 'league/rating.html'}, name='league_rating'),
    url(r'^leagues/(?P<league_id>\d+)/games/$', 'league.views.league_games', {'template_name': 'league/games.html'}, name='league_games'),
    url(r'^leagues/(?P<league_id>\d+)/results/$', 'league.views.league_results', {'template_name': 'league/results.html'}, name='league_results'),
    url(r'^leagues/(?P<league_id>\d+)/penalties/$', 'league.views.league_penalties', {'template_name': 'league/penalties.html'}, name='league_penalties'),
    url(r'^leagues/(?P<league_id>\d+)/competitors/(?P<competitor_id>\d+)/gamerivals/$', 'league.views.competitor_game_rivals',{'template_name': 'league/competitor_game_rivals.html'}, name='competitor_game_rivals'),

    url(r'^leagues/statement/$', 'league.views.flatpage', name='league_statement'),
    url(r'^leagues/rules/$', 'league.views.flatpage', name='league_rules'),

    url(r'^i18n/setlang/', lang_view.set_language),


    #API not for MENU
    url(r'^leagues/(?P<league_id>\d+)/competitors/(?P<competitor_id>\d+)/opponents/$', 'league.views.competitor_opponents', name='competitor_opponents'),


    #url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/league/(?P<league_id>\d+)/game/add', 'league.views.add_game', name='add_game'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^rosetta/', include('rosetta.urls')),
    #url(r'^admin_tools/', include('admin_tools.urls')),

    url(r'^api/v0/', include(router.urls)),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
    pass
