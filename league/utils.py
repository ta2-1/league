from datetime import timedelta, datetime
from functools import wraps
import logging
import re

from django.core.cache import caches
from django.db.models import Q
from django.utils import timezone


cache = caches['league']


def statslog(function):
    @wraps(function)
    def _statslog(instance, *args, **kwargs):
        start = timezone.now()
        result = function(instance, *args, **kwargs)
        end = timezone.now()
        logger = logging.getLogger('league')
        logger.info("%s\t%s\t%s\t%s" % (function.__name__, ', '.join(map(lambda x: str(x), args)), end - start,
                            instance))
        return result
    return _statslog

def statslog_func(function):
    @wraps(function)
    def _statslog(*args, **kwargs):
        start = timezone.now()
        result = function(*args, **kwargs)
        end = timezone.now()
        logger = logging.getLogger('league')
        logger.info("%s\t%s\t%s" % (function.__name__, ', '.join(map(lambda x: str(x), args)), end - start))
        return result
    return _statslog

def leaguecompetitor_getfromcache(function):
    def _getfromcache(instance, *args, **kwargs):
        if 'date_time' in kwargs:
            date_time = kwargs['date_time']
        elif args:
            date_time = args[0]
        else:
            date_time = None

        last_game = instance.last_game(date_time)
        if last_game is None:
            date = instance.league.start_date
        else:
            date = last_game.end_datetime
        date =  date.strftime("%Y-%m-%d")
        key = '%s:%s:%s' % (instance.id, function.__name__, date)
       
        result = cache.get(key)
        if result is None:
            result = function(instance, *args, **kwargs)
            cache.set(key, result, 60 * 60 * 24 * 30 * 6)
        return result
    return _getfromcache

def league_get_N(settings, result1, result2):
    try:
        return eval(settings.n_formula)
    except:
        return result1 - result2
    
def league_get_DELTA(settings, r1, r2, N, min_rival_count=0):
    SOFTEN_COEF = settings.soften_coef
    TRUST_COEF = 0.25 + 0.05*min_rival_count
    TRUST_DELTA = min_rival_count if min_rival_count < 15 else 15

    try:
        return eval(settings.delta_formula)
    except:
        return TRUST_COEF*(N + (r2-r1)/(SOFTEN_COEF-TRUST_DELTA))
    
def get_new_delta(settings, rating1, rating2):
    game = rating1.game
    if game.no_record:
        return 0
    else:
        result1 = rating1.game.get_player_result(rating1.player)
        result2 = rating2.game.get_player_result(rating2.player)
        lc1 = rating1.league.leaguecompetitor_set.get(competitor=rating1.player)
        lc2 = rating2.league.leaguecompetitor_set.get(competitor=rating2.player)

        min_rival_count = min(lc1.rival_count(game.start_datetime), lc2.rival_count(game.start_datetime))
        n = league_get_N(settings, result1, result2)
     
        return league_get_DELTA(settings, rating1.rating_before, rating2.rating_before, n, min_rival_count)
    
@statslog_func
def update_rating_after(rating):
    from league.models import Rating

    r1 = Rating.objects.filter(league=rating.league, player=rating.player, datetime__gt=rating.datetime).order_by('datetime')[:1]
    if r1:
        r1 = r1[0]
        before_changed = False
        if r1.rating_before != rating.rating_after:
            r1.rating_before = rating.rating_after
            before_changed = True
        r2 = None
        new_delta = r1.delta
        if r1.type == 'game':
            r2 = Rating.objects.get(Q(game=r1.game) & ~Q(id=r1.id))
            new_delta = get_new_delta(rating.league.settings, r1, r2)
        if before_changed or r1.delta != new_delta:  
            r1.delta = new_delta    
            r1.save()
            if r2 is not None:
                r2.delta = 0-new_delta
                r2.save()
            
def get_place_interval(place):
    if place is None:
        return (-1, -1)

    if re.match(r'^\d+$', place) != None:
        return (int(place), int(place))
    else:
        places = re.match(r'(\d+)\s*-\s*(\d+)', place)
        if places != None:
            return (int(places.group(1)), int(places.group(2)))
        else:
            return (-1, -1)
            

def get_league_rating_datetime(dt):
    return dt.replace(hour=0, minute=0, second=0) + timedelta(days=1)
