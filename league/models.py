# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q, Count

from rating.models import Competitor, Location
from rating.utils import get_place_from_rating_list, get_place
from league.utils import league_get_N, league_get_DELTA, update_rating_after, get_place_interval
        
from datetime import datetime, timedelta, time
from league.utils import get_league_rating_datetime, statslog, leaguecompetitor_getfromcache

from django.utils.translation import ugettext_lazy as _

from django.core.cache import get_cache


RATING_CHANGE_TYPE = (
    ('game', _(u'Игра')),
    ('penalty', _(u'Штраф')), 
    ('other', _(u'Другое')), 
)

TOURNAMENT_CATEGORIES = [('A', _(u'Категория А')), ('B', _(u'Категория В')),] 

def get_current_league():
    #return None
    now = datetime.now()
    ll = League.objects.filter(start_date__lt=datetime.now()).order_by('-end_date')[:1]
    if ll.count() == 1:
        return ll[0]
    else:
        return u''

class League(models.Model):
    class Meta:
        verbose_name = u'Лига'
        verbose_name_plural = u'Лиги'
         
    title = models.CharField(u'Название', max_length=255)
    competitors = models.ManyToManyField(Competitor, through='LeagueCompetitor', related_name='leagues')
    
    start_date = models.DateField(verbose_name=u'Дата начала')
    end_date = models.DateField(verbose_name=u'Дата окончания')
    
    tournament_a_datetime = models.DateTimeField(verbose_name=u'Дата и время турнира (A)', blank=True, null=True)
    tournament_b_datetime = models.DateTimeField(verbose_name=u'Дата и время турнира (B)', blank=True, null=True)
    location = models.ForeignKey(Location, verbose_name=u'Место проведения турнира', blank=True, null=True) 
    is_tournament_data_filled = models.BooleanField(verbose_name=u'Данные введены полностью')
    
    settings = models.ForeignKey('LeagueSettings', verbose_name=u'Настройки лиги',)
    visible = models.BooleanField(verbose_name=u'Отображать на сайте', default=True,)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('league_rating', [], {
            'league_id': self.id,
        })
        
    def valid_games(self):
        return self.game_set.filter(no_record=False)

    def get_last_place(self):
        rcl = self.get_rating_competitor_list()
        
        return max(map(lambda x: x['place'], rcl))
        
    def get_last_rating_changed_datetime(self):
        try:
            dt = Rating.objects.filter(league=self).order_by('-datetime')[:1][0].datetime
        except:
            dt = datetime.now()
        
        return dt
                    
    def get_total_rating_competitor_list(self):
        league_date = datetime.combine(self.end_date, time())
        
        rivals_count = self.settings.final_rival_quantity
    
        rcl = filter(lambda x: x['rival_count'] >= rivals_count, self.get_rating_competitor_list(league_date + timedelta(days=3)))
        for i,x in enumerate(rcl):
            base = i+1 if i <= 15 else i-15
            if x['tournament_place'] != '-':
                x['place_delta'] = base - get_place(x['tournament_place'])

        return rcl
    
    def get_rating_competitor_list(self, date_time=None):
        dt_param = datetime.now() if date_time is None else date_time
        
        rivals_count = self.settings.reliability_rival_quantity

        # minus 2 days for getting current state if datetime is now...
        dt = get_league_rating_datetime(dt_param)
        dt_str = dt.strftime("%Y-%m-%d")
        cache_key= u'rating_competitor_list_for_%d_league_%s' % (self.id, dt_str)
        cache = get_cache('league')
        rcl = cache.get(cache_key)
        if rcl is None:           
            lcc = LeagueCompetitor.objects.filter(league__id=self.id)
            
            rcl = map(lambda x: 
                    {
                       'object':x.competitor, 
                       'rating':x.saved_rating(dt), 
                       'place': '-', 
                       'lc': x,
                       'tournament_place': x.tournament_place if x.tournament_place != '' else '-',
                       'sort_tournament_place': get_place(x.tournament_place) if x.tournament_place != '' else '-',
                       'game_count': x.game_count(dt), 
                       'rival_count': x.rival_count(dt),
                       'last_game': x.last_game(dt)
                    }, lcc)                     
            rcl = sorted(rcl, key=lambda x: x['rating'], reverse=True)
            
            rcd = {}
            for x in rcl:
                rcd[x['object'].id] = x  
                   
            vrcl = filter(lambda x: x['rival_count'] >= rivals_count, rcl)
            
            for i,x in enumerate(vrcl):
                place = get_place_from_rating_list(vrcl, i)
                rcd[x['object'].id]['place'] = place
           
            cache.set(cache_key, rcl, 60 * 60 * 24 * 30 * 6)
            
        return rcl
    
    def is_ended(self):
        league_date = datetime.combine(self.end_date, time())
        dt = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=2)
    
        return dt >= league_date

class LeagueTournament(League):
    class Meta:
        proxy = True
        verbose_name = u'Итоговый турнир Лиги'
        verbose_name_plural = u'Итоговые турниры Лиги'
 
class LeagueAlterTournament(League):
    class Meta:
        proxy = True
        verbose_name = u'Итоговый турнир Лиги (2)'
        verbose_name_plural = u'Итоговые турниры Лиги (2)'


class LeagueCompetitor(models.Model):
    class Meta:
        verbose_name = u'Участник лиги'
        verbose_name_plural = u'Участники лиги'
        
    competitor = models.ForeignKey(Competitor, verbose_name=u'Участник')
    league = models.ForeignKey(League, verbose_name=u'Лига')
    paid = models.NullBooleanField(u'Оплатил')
    status = models.CharField(u'Статус', max_length=255, blank=True)
    tournament_place = models.CharField(u'Место', max_length=255, blank=True)
    is_participant = models.BooleanField(u'Принимал участие в турнире', blank=True)
    tournament_category = models.CharField(u'Категория турнира', blank=True, null=True,
                                           choices=TOURNAMENT_CATEGORIES, max_length=4)
    
    def __unicode__(self):
        return u"%s: %s %s" % (self.league.title, self.competitor.lastName, self.competitor.firstName)

    def rating(self, datetime=datetime.now):
        rr = Rating.objects.filter(league=self.league, player=self.competitor, datetime__lt=datetime).order_by('datetime')
        res = self.league.settings.initial_rating
        
        for r in rr:
            res += r.delta
        
        return res
    
    def saved_rating(self, datetime=datetime.now):
        rr = Rating.objects.filter(league=self.league, player=self.competitor, datetime__lt=datetime).order_by('-datetime')[:1]
        res = self.league.settings.initial_rating
        
        if rr:
            res = rr[0].rating_after
        
        return res
    
    # current state means the end of day before yesterday (begining of the yesterday) 
    def current_state_rating(self):
        for x in self.league.get_rating_competitor_list():
            if x['object'].id == self.competitor.id:
                return x['rating']

        
        return None
 
    def place(self):
        for x in self.league.get_rating_competitor_list():
            if x['object'].id == self.competitor.id:
                return x['place']
        
        return None
    
    @leaguecompetitor_getfromcache
    def game_count(self, date_time=None):
        dt = datetime.now() if date_time is None else date_time
        
        return Game.objects.filter(Q(league=self.league, no_record=False, end_datetime__lte=dt)&(Q(player1=self.competitor)|Q(player2=self.competitor))).count()
        
    @leaguecompetitor_getfromcache
    def rival_count(self, date_time=None):
        dt = datetime.now() if date_time is None else date_time
        
        gg = Game.objects.filter(
            Q(league=self.league, end_datetime__lte=dt, no_record=False)&
            (Q(player1=self.competitor)|Q(player2=self.competitor))
        )

        rivals = {}
        for g in gg:
            if g.player1 != self.competitor:
                player = g.player1
            else:
                player = g.player2
            rivals[player.id] = player

        return len(rivals.keys())
        #count = Competitor.objects.filter(
        #    ~Q(id=self.competitor.id)&
        #    (Q(home_game_set__league=self.league)|Q(home_game_set__league__isnull=True))&
        #    (Q(guest_game_set__league=self.league)|Q(guest_game_set__league__isnull=True))&
        #    (Q(home_game_set__in=gg)|Q(guest_game_set__in=gg))
        #).distinct().count()
        #
        #return count

    # for games where no_record is false
    def rivals(self, from_date_time=None, to_date_time=None):
        filter_by = {'league': self.league, 'no_record': False}
        if not from_date_time is None:
            filter_by.update({'end_datetime__gte': from_date_time})
        if not to_date_time is None:
            filter_by.update({'end_datetime__lte': to_date_time})

        gg = Game.objects.filter(
            Q(**filter_by)&
            (Q(player1=self.competitor)|Q(player2=self.competitor))
        )

        rivals = {}
        for g in gg:
            if g.player1 != self.competitor:
                player = g.player1
            else:
                player = g.player2
            rivals[player.id] = player

        return rivals.values()

        #return Competitor.objects.filter(
        #    ~Q(id=self.competitor.id)&
        #    (Q(home_game_set__league=self.league)|Q(home_game_set__league__isnull=True))&
        #    (Q(guest_game_set__league=self.league)|Q(guest_game_set__league__isnull=True))&
        #    (Q(home_game_set__in=gg)|Q(guest_game_set__in=gg))
        #).distinct()

    def last_game(self, date_time=None):
        dt = datetime.now() if date_time is None else date_time
        
        gg = Game.objects.filter(Q(league=self.league, end_datetime__lte=dt) & (Q(player1=self.competitor)|Q(player2=self.competitor))).order_by('-end_datetime')[:1]
        
        if gg:
            return gg[0]
        else:
            return None
            
    def get_delta_rating(self, game):
        try:
            d = Rating.objects.get(game=game, league=self.league, player=self.competitor)
        except:
            d = 0
        
        return d
    
    def get_tournament_category(self):
        trcl = self.league.get_total_rating_competitor_list()
        place = -1
        for i, x in enumerate(trcl):
            if x['lc'].id == self.id:
                place = i+1
                break
        
        if place >= 0:
            return 'A' if place <= 16 else 'B'
        else: 
            return ''

    @statslog
    def get_possible_opponents(self, dt=None):
        rcl = self.league.get_rating_competitor_list(dt)
        f_rcl = filter(lambda x: x['place'].isdigit(), rcl)
        (min_p, max_p) = get_place_interval(self.place())
        last_place = max(map(lambda x: int(x['place']), f_rcl)) if len(f_rcl) > 0 else 0
        offset = self.league.settings.position_difference / 2 
        def contains(min_p, max_p, x, last_place, offset):
            if min_p == -1 and max_p == -1:
                return True 
            
            (min_x, max_x) = get_place_interval(x['place'])
            extra_minus, extra_plus = (0, 0)
            
            if min_p - offset <= 0:
                extra_plus = offset - min_p + 1
            if max_p + offset > last_place:
                extra_minus = max_p + offset - last_place 
                
            return (max_x == -1 and min_x == -1) or (min_p - offset - extra_minus <= min_x and max_p + offset + extra_plus >= max_x)
        
        res = filter(lambda x: x['object'].id != self.competitor.id and contains(min_p, max_p, x, last_place, offset), rcl)
        
        return sorted(res, key=lambda x: x['object'].lastName)
    
class Game(models.Model):
    class Meta:
        verbose_name = u'Игра'
        verbose_name_plural = u'Игры'
        
    player1 = models.ForeignKey(Competitor, verbose_name=u'Игрок1', related_name='home_game_set')
    player2 = models.ForeignKey(Competitor, verbose_name=u'Игрок2', related_name='guest_game_set')
    
    start_datetime = models.DateTimeField(verbose_name=u'Дата и время начала', blank=True)
    end_datetime = models.DateTimeField(verbose_name=u'Дата и время окончания')
    
    location = models.ForeignKey(Location, verbose_name=u'Место проведения') 
    
    result1 = models.SmallIntegerField(u'Счёт')
    result2 = models.SmallIntegerField(u' ')
    
    league = models.ForeignKey(League, verbose_name=u'Лига', default=get_current_league)
    no_record = models.BooleanField(verbose_name=u'Незачетная игра')

    def __unicode__(self):
        return u"%s - %s (%d : %d) - %s" % (self.player1.lastName, self.player2.lastName, self.result1, self.result2, self.end_datetime)
    
    def save(self, *args, **kwargs):
        self.start_datetime = self.end_datetime
        super(Game, self).save(*args, **kwargs)
        
        if self.result1 > 0 or self.result2 > 0:
            lc1 = LeagueCompetitor.objects.get(league=self.league, competitor=self.player1)
            lc2 = LeagueCompetitor.objects.get(league=self.league, competitor=self.player2)
            (r1, r2) = map(lambda x: x.rating(self.end_datetime), (lc1, lc2))
            date = self.end_datetime.strftime("%Y-%m-%d") 
            if self.no_record:
                delta = 0
            else:
                cache = get_cache('league')
                cache.delete('%s:%s:%s' % (lc1.id, 'rival_count', date))
                cache.delete('%s:%s:%s' % (lc2.id, 'rival_count', date))
                cache.delete('%s:%s:%s' % (lc1.id, 'game_count', date))
                cache.delete('%s:%s:%s' % (lc2.id, 'game_count', date))


                min_rival_count = min(lc1.rival_count(), lc2.rival_count())
                n = league_get_N(self.league.settings, self.result1, self.result2)
                delta = league_get_DELTA(self.league.settings, r1, r2, n, min_rival_count)
               
            if Rating.objects.filter(league=self.league, game=self).count() == 0:
                rating1 = Rating(league=self.league, type='game', game=self, datetime=self.end_datetime, player=self.player1, delta=delta, rating_before=r1)
                rating2 = Rating(league=self.league, type='game', game=self, datetime=self.end_datetime, player=self.player2, delta=0-delta, rating_before=r2)
            else:
                rating1 = Rating.objects.get(league=self.league, game=self, player=self.player1)
                rating2 = Rating.objects.get(league=self.league, game=self, player=self.player2)
                rating1.delta = delta
                rating2.delta = 0-delta
                
            rating1.save()
            rating2.save()
            
            
    def get_player_result(self, player):
        if player == self.player1:
            return self.result1
        else:
            return self.result2
         
    
    
class Rating(models.Model):
    class Meta:
        verbose_name = u'Изменение рейтинга'
        verbose_name_plural = u'Изменения рейтинга'
    
    league = models.ForeignKey(League, verbose_name=u'Лига')
    type = models.CharField(verbose_name=u'Причина изменения рейтинга', choices=RATING_CHANGE_TYPE, max_length=25)
    game = models.ForeignKey(Game, verbose_name=u'Игра', blank=True, null=True)
    datetime = models.DateTimeField(verbose_name=u'Дата')

    comment = models.TextField(verbose_name=u'Комментарий')

    player = models.ForeignKey(Competitor, verbose_name=u'Игрок')
    delta = models.FloatField(u'Изменение')
    rating_before = models.FloatField(u'Рейтинг "До"')
    rating_after = models.FloatField(u'Рейтинг "После"')
    
    def save(self, *args, **kwargs):
        self.rating_after = self.rating_before + self.delta
        super(Rating, self).save(*args, **kwargs)
        update_rating_after(self)
        cache = get_cache('league')
        dt_str = self.datetime.strftime("%Y-%m-%d")
        cache_key= u'rating_competitor_list_for_%d_league_%s' % (self.id, dt_str)
        cache.delete(cache_key)

    def __unicode__(self):
        return u"%s (%f) - %s" % (self.player.lastName, self.delta, self.datetime) 


class LeagueSettings(models.Model):
    class Meta:
        verbose_name = u'Настройки лиги'
        verbose_name_plural = u'Настройки лиги'

    title = models.CharField(
        max_length=255,
        verbose_name=u'Наименование',
    )
    soften_coef = models.PositiveIntegerField(
        verbose_name=u'Смягчающий коэффициент',
        default=20,
    )
    position_difference = models.PositiveIntegerField(
        verbose_name=u'Допустимая разница в занимаемых позициях',
        default=10
    )
    initial_rating = models.PositiveIntegerField(
        verbose_name=u'Начальный рейтинг',
        default=100,
    )
    reliability_rival_quantity = models.PositiveIntegerField(
        verbose_name=u'Необходимое количество соперников для присвоения места',              
        default=4,
    )
    final_rival_quantity = models.PositiveIntegerField(
        verbose_name=u'Необходимое количество соперников для присвоения итогового места',              
        default = 10,
    )
    n_formula = models.CharField(
        max_length=255,
        verbose_name=u'Формула N',
        default = 'result1 - result2',
    )
    delta_formula = models.CharField(
        max_length=255,
        verbose_name=u'Формула DELTA',              
        default = 'N + (r2-r1)/SOFTEN_COEF',
    )

    def __unicode__(self):
        return u"%s" % self.title 


