from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.conf import settings

from rating.models import Competitor
from league.models import get_current_league, Game, League, LeagueCompetitor, Rating
from django.db.models import Q
from league.utils import league_get_N, league_get_DELTA, get_league_rating_datetime

from django.contrib.flatpages.models import FlatPage

from datetime import datetime, timedelta, time

#from django.views.decorators.cache import cache_control
from django.views.decorators.cache import never_cache

@never_cache
def flatpage(request, template_name='league/flatpage.html'):
    url = request.path_info
    if not url.startswith('/'):
        url = "/" + url
        
    f = get_object_or_404(FlatPage, url__exact=url, sites__id__exact=settings.SITE_ID)
    
    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'flatpage': f, 
    },)
    
    return HttpResponse(t.render(c))
    
@never_cache
def leagues(request):
    league = get_current_league()
    
    if not league.is_ended():
        return redirect(getattr(settings, 'FORCE_SCRIPT_NAME', '') + '/leagues/%d' % league.id)
    else:
        return redirect(getattr(settings, 'FORCE_SCRIPT_NAME', '') + '/leagues/%d/results' % league.id )
    
@never_cache
def league_list(request, template_name):
    return object_list(request, League.objects.filter(visible=True), template_name=template_name)

@never_cache
def league_rating(request, league_id, template_name):
    league = League.objects.get(id=league_id)
    
    try:
        if request.GET.has_key('date'): 
            date = datetime.strptime(request.GET['date'], '%d.%m.%Y')
            
            dt = date.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        else:
            dt = datetime.now().replace(hour=0, minute=0, second=0)
    except:
        dt = datetime.now().replace(hour=0, minute=0, second=0)
    
    rcl = league.get_rating_competitor_list(dt)
    
    t = loader.get_template(template_name)

    c = RequestContext(request, {
        'league': league,
        'rcl': rcl, 
        'league_rating_datetime': dt - timedelta(days=1)
    },)
    
    return HttpResponse(t.render(c))

@never_cache
def league_results(request, league_id, template_name):
    league = League.objects.get(id=league_id)
   
    if not league.is_ended():
        return redirect('/leagues/%s' % league.id)

    rcl = league.get_total_rating_competitor_list()

    t = loader.get_template(template_name)
    if league.is_tournament_data_filled:
        rcl_a = filter(lambda x: x['lc'].tournament_category == 'A', rcl)
        rcl_b = filter(lambda x: x['lc'].tournament_category == 'B', rcl)
    else:
        rcl_a = rcl[:16]
        rcl_b = rcl[16:]

    c = RequestContext(request, {
        'league': league,
        'rcl_a': rcl_a,
        'rcl_b': rcl_b,
        },)
    
    return HttpResponse(t.render(c))

@never_cache
def league_games(request, league_id, template_name):
    league = League.objects.get(id=league_id)
    games = sorted(Game.objects.filter(league__id=league_id), key=lambda x: x.end_datetime)
    num = 0
    for game in games:
        if not game.no_record:
            num += 1
            game.number = num

    t = loader.get_template(template_name)

    c = RequestContext(request, {
        'league': league,
        'object_list': games,
    },)
    
    return HttpResponse(t.render(c))

@never_cache
def league_penalties(request, league_id, template_name):
    league = League.objects.get(id=league_id)
    rr = Rating.objects.filter(league__id=league_id, type='penalty').order_by('datetime')
    t = loader.get_template(template_name)

    c = RequestContext(request, {
        'league': league,
        'object_list': rr,
    },)
    
    return HttpResponse(t.render(c))

@never_cache
def competitor(request, league_id, competitor_id, template_name):
    leaguecompetitors = LeagueCompetitor.objects.filter(league__visible=True, competitor__id=competitor_id).order_by('league__start_date')
    leaguecompetitor = get_object_or_404(LeagueCompetitor, league__id=league_id, competitor__id=competitor_id)
    
    i = 1
    rr = list(Rating.objects.filter(player__id=competitor_id, league__id=league_id).order_by('datetime'))
    for r in rr:
        r.number = i
        if (r.type == 'game' and not r.game.no_record):
            i += 1
    rr = list(reversed(rr))
    
    # add penalties
    #rr = Rating.objects.filter(player__id=competitor_id, type='game', league__id=league_id).order_by('-datetime')
    
    #games = Game.objects.filter(Q(player1__id=competitor_id)|Q(player2__id=competitor_id), league__id=league_id).order_by('-end_datetime')
    #r_games = map(lambda x: {'game': x, 'delta': leaguecompetitor.get_delta_rating(x)}, games)
    extra_context={'rr': rr, 'leaguecompetitors': leaguecompetitors, 'leaguecompetitor': leaguecompetitor}
    
    return object_detail(request, Competitor.objects.all(), competitor_id, extra_context=extra_context, template_name=template_name)

@never_cache
def competitor_leagues(request, competitor_id):
    league_id = get_current_league().id
    lc = None
    try:
        lc = LeagueCompetitor.objects.get(league__id=league_id, competitor__id=competitor_id)
    except:
        lcc = LeagueCompetitor.objects.filter(competitor__id=competitor_id).order_by('-league__id')
        if lcc.count() > 0:
            league_id = lcc[0].league.id

    return redirect('/competitors/%s/leagues/%s' % (competitor_id, league_id))

@never_cache
def competitor_league_list(request, competitor_id, template_name):
    leaguecompetitors = LeagueCompetitor.objects.filter(competitor__id=competitor_id).order_by('league__start_date')
    
    return object_detail(request, Competitor.objects.all(), competitor_id, extra_context={'leaguecompetitors': leaguecompetitors}, template_name=template_name)
    
@never_cache
def competitors_vs(request, competitor1_id, competitor2_id, template_name):
    games = Game.objects.filter(Q(player1__id=competitor1_id, player2__id=competitor2_id)|Q(player1__id=competitor2_id, player2__id=competitor1_id), league__visible=True).order_by('-end_datetime')
    
    return object_detail(request, Competitor.objects.all(), competitor1_id, extra_context={'opponent': get_object_or_404(Competitor, id=competitor2_id) ,'games': games}, template_name=template_name)

@never_cache
def competitor_rivals(request, competitor_id, template_name):
    league_id = get_current_league().id
    
    try:
        lc = LeagueCompetitor.objects.get(league__id=league_id, competitor__id=competitor_id)
    except:
        lcc = LeagueCompetitor.objects.filter(competitor__id=competitor_id).order_by('-league__id')
        if lcc.count() > 0:
            lc = lcc[0]
        else:
            lc = get_object_or_404(LeagueCompetitor, league__id=league_id, competitor__id=competitor_id)

    games = Game.objects.filter(Q(player1__id=competitor_id)|Q(player2__id=competitor_id))
    games = games.filter(league__visible=True)
    rivals = {}
    
    for g in games:
        if g.player1.id != int(competitor_id):
            wins = 1 if g.result1 > g.result2 else 0
            player = g.player1
        else:
            wins = 1 if g.result2 > g.result1 else 0
            player = g.player2        
            
        if not rivals.has_key(player.id):
            rivals[player.id] = {'object': player, 'wins': wins, 'games_count': 1}
        else:
            rivals[player.id]['wins'] += wins
            rivals[player.id]['games_count'] += 1
              
    rivals = sorted(map(lambda x: x[1], rivals.items()), key=lambda x: x['object'].lastName)
        
    return object_detail(request, Competitor.objects.all(), competitor_id, extra_context={'rivals': rivals, 'lc': lc}, template_name=template_name)

def get_possible_opponents(lc, dt=None):
    if dt is None:
        dt = get_league_rating_datetime(datetime.now())
    o1 = lc.get_possible_opponents(dt)
    o2 = lc.get_possible_opponents(dt - timedelta(days=1))

    d = {}
    for x in o1:
        d[x['object'].id] = x
    for x in o2:
        if not d.has_key(x['object'].id):
            d[x['object'].id] = x 
     
    return sorted(d.values(), key=lambda x: x['object'].lastName)

def get_game_delta(settings, rating1, rating2, result1, result2, min_rival_count):
    n = league_get_N(settings, result1, result2)
    
    return league_get_DELTA(settings, rating1, rating2, n, min_rival_count)

def get_element_rating(rcl, x):
    for r in rcl:
        if r['object'].id == x['object'].id:
            return r['rating']

    return None

@never_cache
def competitor_game_rivals(request, league_id, competitor_id, template_name):
    lc = get_object_or_404(LeagueCompetitor, league__id=league_id, competitor__id=competitor_id)
    rival_count = lc.rival_count()
    # get live rating for actual deltas
    live_rcl = lc.league.get_rating_competitor_list(datetime.now()+timedelta(days=2))    
    dt = datetime.now().replace(hour=3, minute=0, second=0)
    rcl = lc.league.get_rating_competitor_list(dt)
    rivals = get_possible_opponents(lc, dt)

    for r in rivals:
        r['rating'] = get_element_rating(rcl, r)
        r['live_rating'] = get_element_rating(live_rcl, r)

    rivals = sorted(rivals, key=lambda x: -1 * x['live_rating'])

    for r in rivals:
        r['results'] = []
        min_rival_count = min(rival_count, r['lc'].rival_count()) 
        for res2 in range(3):
            r['results'].append({'res1' : 3, 'res2' : res2, 'delta': get_game_delta(lc.league.settings, lc.rating(), r['live_rating'], 3, res2, min_rival_count)})
        for res1 in reversed(range(3)):
            r['results'].append({'res1' : res1, 'res2' : 3, 'delta': get_game_delta(lc.league.settings, lc.rating(), r['live_rating'], res1, 3, min_rival_count)})

    return object_detail(request, Competitor.objects.all(), competitor_id, extra_context={'rivals': rivals, 'lc': lc}, template_name=template_name)


import json 

@never_cache
def competitor_opponents(request, league_id, competitor_id):
    lc = get_object_or_404(LeagueCompetitor, league__id=league_id, competitor__id=competitor_id)
    #lc = LeagueCompetitor.objects.get(league__id=league_id, competitor__id=competitor_id)
    #json_data = json.dumps(map(lambda x: x['object'].id, lc.get_possible_opponents()))
    
    try:
        if request.GET.has_key('date'): 
            date = datetime.strptime(request.GET['date'], '%d.%m.%Y')
            
            dt = date.replace(hour=3, minute=0, second=0)
        else:
            dt = None
    except:
        dt = None
    
    r = get_possible_opponents(lc, dt)
    ol = map(lambda x: {'id': x['object'].id, 'name': u'%s %s' % (x['object'].lastName, x['object'].firstName )}, r)
    
    json_data = json.dumps({'HTTPRESPONSE':1, 'data': ol}, ensure_ascii=False)
    
    return HttpResponse(json_data, mimetype="application/json")
