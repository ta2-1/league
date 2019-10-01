# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time

from django.contrib.flatpages.models import FlatPage
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_rq import job

from phonenumber_field.modelfields import PhoneNumberField

from rating.models import Competitor, Location
from rating.utils import get_place
from league.utils import (league_get_N, league_get_DELTA,
                          update_rating_after, get_place_interval)
from league.utils import (empty2dash, get_league_rating_datetime, statslog,
                          leaguecompetitor_getfromcache,
                          clear_cache_on_game_save, get_rating_competitor_list,
                          get_month_interval)


RATING_CHANGE_TYPE = (
    ('game', _(u'Игра')),
    ('penalty', _(u'Штраф')), 
    ('other', _(u'Другое')), 
)

TOURNAMENT_CATEGORIES = [('A', _(u'Категория А')), ('B', _(u'Категория В')),] 


def get_current_leagues():
    return list(League.objects.filter(is_current=True))


class LeagueGroup(models.Model):
    class Meta:
        verbose_name = u'Группа лиг'
        verbose_name_plural = u'Группы лиг'

    title = models.CharField(
        max_length=255,
        verbose_name=u'Наименование',
    )
    slug = models.CharField(u'Код', max_length=25)

    statement = models.ForeignKey(
        FlatPage,
        verbose_name=u'Положение лиги',
        related_name='stated_league_group',
        null=True)
    rules = models.ForeignKey(
        FlatPage,
        verbose_name=u'Правила расчета рейтинга',
        related_name='ruled_league_group',
        null=True)
    visible = models.BooleanField(
        verbose_name=u'Отображать на сайте',
        default=True,
    )
    is_current = models.BooleanField(
        verbose_name=u'Текущая',
        default=False,
    )

    def __unicode__(self):
        return u"%s" % self.title


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
        verbose_name=u'Необходимое количество соперников для присвоения '
                     u'итогового места',
        default=10,
    )
    n_formula = models.CharField(
        max_length=255,
        verbose_name=u'Формула N',
        default='result1 - result2',
    )
    delta_formula = models.CharField(
        max_length=255,
        verbose_name=u'Формула DELTA',
        default='N + (r2-r1)/(SOFTEN_COEF-TRUST_DELTA)',
    )
    rating_off_last_days = models.PositiveIntegerField(
        verbose_name=u'Количество последних дней лиги, когда результаты '
                     u'накапливаются, но рейтинг не обновляется',
        default=4,
    )

    def __unicode__(self):
        return u"%s" % self.title


class League(models.Model):
    class Meta:
        verbose_name = u'Лига'
        verbose_name_plural = u'Лиги'
         
    title = models.CharField(u'Название', max_length=255)
    competitors = models.ManyToManyField(
        Competitor,
        through='LeagueCompetitor',
        related_name='leagues'
    )
    division = models.IntegerField(u'Номер дивизиона', null=True)
    group = models.ForeignKey(LeagueGroup, null=True)

    start_date = models.DateField(verbose_name=u'Дата начала')
    end_date = models.DateField(verbose_name=u'Дата окончания')

    settings = models.ForeignKey(
        LeagueSettings,
        verbose_name=u'Настройки лиги',
    )
    visible = models.BooleanField(
        verbose_name=u'Отображать на сайте',
        default=True,
    )
    is_current = models.BooleanField(
        verbose_name=u'Текущая',
        default=False,
    )
    mark_unpaid_competitors = models.BooleanField(
        verbose_name=u'Отмечать неоплативших',
        default=False,
    )
    statement = models.ForeignKey(
        FlatPage,
        verbose_name=u'Положение лиги',
        related_name='stated_leagues',
        null=True)
    rules = models.ForeignKey(
        FlatPage,
        verbose_name=u'Правила расчета рейтинга',
        related_name='ruled_leagues',
        null=True)

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
            dt = Rating.objects.filter(
                league=self
            ).order_by('-datetime')[:1][0].datetime
        except:
            dt = timezone.now()
        
        return dt

    def get_rating_competitor_list(self, date_time=None):
        dt_param = timezone.now() if date_time is None else date_time

        rivals_count = self.settings.reliability_rival_quantity

        dt = get_league_rating_datetime(dt_param)
        dt_str = dt.strftime("%Y-%m-%d")
        cache_key= u'rating_competitor_list_for_%d_league_%s' % (
            self.id, dt_str)
        cache = caches['league']
        rcl = cache.get(cache_key)
        if rcl is None:
            lcc = LeagueCompetitor.objects.filter(
                league__id=self.id
            ).select_related('league', 'competitor')
            rcl = get_rating_competitor_list(lcc, rivals_count, date_time=dt)
            cache.set(cache_key, rcl, 60 * 60 * 24 * 30 * 6)

        return rcl
    
    def is_ended(self):
        league_date = datetime.combine(self.end_date, time())
        dt = timezone.make_naive(
            timezone.now().replace(hour=0, minute=0, second=0)
        ) - timedelta(days=2)
    
        return dt >= league_date

    def get_rating_off_dt(self):
        rating_off_dt = datetime.combine(
            self.end_date,
            time=time()
        ) - timedelta(
            days=self.settings.rating_off_last_days - 1
        )
        tz = timezone.get_default_timezone()
        rating_off_dt = timezone.make_aware(rating_off_dt, tz)

        return rating_off_dt

    @property
    def current_rating_datetime(self):
        dt = timezone.now()

        return dt.replace(hour=0, minute=0, second=0, microsecond=0)


class LeagueTournament(League):
    class Meta:
        proxy = True
        verbose_name = u'Итоговый турнир Лиги'
        verbose_name_plural = u'Итоговые турниры Лиги'


class LeagueTournamentWithSets(League):
    class Meta:
        proxy = True
        verbose_name = u'Итоговый турнир Лиги (Категории)'
        verbose_name_plural = u'Итоговые турниры Лиги (Категории)'


class LeagueCompetitorManager(models.Manager):
    def get_queryset(self):
        return super(LeagueCompetitorManager, self).get_queryset().filter(is_moved=False)


class LeagueCompetitorWithMovedManager(models.Manager):
    def get_queryset(self):
        return super(LeagueCompetitorWithMovedManager, self).get_queryset()


class LeagueCompetitor(models.Model):
    class Meta:
        verbose_name = u'Участник лиги'
        verbose_name_plural = u'Участники лиги'
        unique_together = ('competitor', 'league')

    competitor = models.ForeignKey(Competitor, verbose_name=u'Участник')
    league = models.ForeignKey(League, verbose_name=u'Лига')
    paid = models.BooleanField(u'Оплатил', default=False)
    status = models.CharField(u'Статус', max_length=255, blank=True)
    phone = PhoneNumberField(u'Телефон', blank=True, null=True)
    tournament_set = models.ForeignKey('LeagueTournamentSet', verbose_name=u'Катерория турнира', null=True, blank=True)
    tournament_place = models.CharField(_(u'Место'), max_length=255, blank=True)
    is_participant = models.BooleanField(_(u'Принимал участие в турнире'), blank=True, default=False)
    is_moved = models.BooleanField(_(u'Перемещен в другую лигу'), blank=True, default=False)

    objects = LeagueCompetitorManager()
    objects_with_moved = LeagueCompetitorWithMovedManager()

    def __unicode__(self):
        return u"%s: %s %s" % (self.league.title, self.competitor.lastName,
                               self.competitor.firstName)

    def first_name(self):
        return self.competitor.firstName

    def last_name(self):
        return self.competitor.lastName

    def rating(self, dt=timezone.now()):
        rating_off_dt = self.league.get_rating_off_dt()
        if dt > rating_off_dt and not self.league.show_last_days_results:
            dt = rating_off_dt

        rr = Rating.objects.filter(
            league=self.league,
            player=self.competitor
        ).filter(
            Q(type='penalty', datetime__lte=dt)|
            Q(datetime__lt=dt)
        ).order_by('datetime')

        res = self.league.settings.initial_rating
        for r in rr:
            res += r.delta
        
        return res
    
    def saved_rating(self, datetime=timezone.now()):
        rr = Rating.objects.filter(
            league=self.league,
            player=self.competitor
        ).filter(
            Q(type='penalty', datetime__lte=datetime)
            | Q(datetime__lt=datetime)
        ).order_by('-datetime')[:1]

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
        dt = timezone.now() if date_time is None else date_time
        
        return Game.objects.filter(
            Q(
                league=self.league,
                no_record=False,
                end_datetime__lte=dt
            ) & (
                Q(player1=self.competitor) | Q(player2=self.competitor)
            )
        ).count()
        
    @leaguecompetitor_getfromcache
    def rival_count(self, date_time=None):
        dt = timezone.now() if date_time is None else date_time
        
        gg = Game.objects.filter(
            Q(
                league=self.league,
                end_datetime__lte=dt,
                no_record=False,
                rating__isnull=False
            ) & (
                Q(player1=self.competitor) | Q(player2=self.competitor)
            )
        )

        rivals = {}
        for g in gg:
            if g.player1 != self.competitor:
                player = g.player1
            else:
                player = g.player2
            rivals[player.id] = player

        return len(rivals.keys())

    def game_count_with(self, rival, date_time=None):
        dt = timezone.now() if date_time is None else date_time

        gg = Game.objects.filter(
            Q(
                league=self.league,
                end_datetime__lte=dt,
                no_record=False,
                rating__isnull=False
            ) & (
                Q(player1=self.competitor, player2=rival) | Q(player2=self.competitor, player1=rival)
            )
        )
        return gg.count()

    def rival_count_in_month(self, date_time=None):
        dt = timezone.now() if date_time is None else date_time
        start_dt, end_dt = get_month_interval(dt)
        gg = Game.objects.filter(
            Q(
                league=self.league,
                end_datetime__gte=start_dt,
                end_datetime__lte=end_dt,
                no_record=False,
                rating__isnull=False
            ) & (
                Q(player1=self.competitor) | Q(player2=self.competitor)
            )
        )

        rivals = {}
        for g in gg:
            if g.player1 != self.competitor:
                player = g.player1
            else:
                player = g.player2
            rivals[player.id] = player

        return len(rivals.keys())

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

    def last_game(self, date_time=None):
        dt = timezone.now() if date_time is None else date_time
        
        gg = Game.objects.filter(
            Q(league=self.league, end_datetime__lte=dt) & (
                Q(player1=self.competitor) | Q(player2=self.competitor)
            )
        ).order_by('-end_datetime', '-id')[:1]
        
        if gg:
            return gg[0]
        else:
            return None
            
    def get_delta_rating(self, game):
        try:
            d = Rating.objects.get(
                game=game,
                league=self.league,
                player=self.competitor
            )
        except:
            d = 0
        
        return d
    
    def get_tournament_category(self):
        trcl = self.league.get_total_rating_competitor_list()
        place = -1
        for i, x in enumerate(trcl):
            if x['lc'].id == self.id:
                place = i + 1
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
    creation_datetime = models.DateTimeField(verbose_name=u'Дата создания', auto_now_add=True, null=True)

    location = models.ForeignKey(Location, verbose_name=u'Место проведения') 
    
    result1 = models.SmallIntegerField(u'Счёт')
    result2 = models.SmallIntegerField(u' ')
    
    league = models.ForeignKey(League, verbose_name=u'Лига')
    no_record = models.BooleanField(verbose_name=u'Незачетная игра', default=False)
    added_via_api = models.BooleanField(verbose_name=u'Добавлена через API', default=False)

    def __unicode__(self):
        return u"%s - %s (%d : %d) - %s" % (
            self.player1.lastName,
            self.player2.lastName,
            self.result1,
            self.result2,
            timezone.localtime(self.end_datetime)
        )

    def clean(self):
        player1_is_winner = self.result1 in [2, 3] and self.result2 < self.result1
        player2_is_winner = self.result2 in [2, 3] and self.result1 < self.result2
        if not (player1_is_winner or player2_is_winner) and self.result1 >= 0 and self.result2 >= 0:
            raise ValidationError(
                {'result1': 'Game final score is incorrect.', 'result2': 'Game final score is incorrect.'})

    def save(self, *args, **kwargs):
        self.start_datetime = self.end_datetime
        self.full_clean()
        need_update_rating = False
        if kwargs.has_key('update_rating'):
            need_update_rating = kwargs['update_rating']
            del kwargs['update_rating']

        super(Game, self).save(*args, **kwargs)
        clear_cache_on_game_save(self)

        if (self.result1 > 0 or self.result2 > 0) and need_update_rating:
            self.update_rating()
            
    def get_player_result(self, player):
        if player == self.player1:
            return self.result1
        else:
            return self.result2

    @property
    def rating_delta(self):
        return Rating.objects.get(player=self.player1, game=self).delta

    def update_rating(self):
        #update_rating_job.delay(self)
        update_rating_job(self)


#@job
def update_rating_job(game):
    lc1 = LeagueCompetitor.objects.get(league=game.league, competitor=game.player1)
    lc2 = LeagueCompetitor.objects.get(league=game.league, competitor=game.player2)
    (r1, r2) = map(lambda x: x.rating(game.end_datetime), (lc1, lc2))
    date = game.end_datetime.strftime("%Y-%m-%d")
    if game.no_record:
        delta = 0
    else:
        cache = caches['league']
        cache.delete('%s:%s:%s' % (lc1.id, 'rival_count', date))
        cache.delete('%s:%s:%s' % (lc2.id, 'rival_count', date))
        cache.delete('%s:%s:%s' % (lc1.id, 'game_count', date))
        cache.delete('%s:%s:%s' % (lc2.id, 'game_count', date))

        min_rival_count = min(lc1.rival_count_in_month(game.start_datetime),
                              lc2.rival_count_in_month(game.start_datetime))
        between_count = lc1.game_count_with(lc2.competitor, game.start_datetime)
        n = league_get_N(game.league.settings, game.result1, game.result2)
        is_max_of_3 = max([game.result1, game.result2]) == 2
        delta = league_get_DELTA(game.league.settings, r1, r2, n, min_rival_count, between_count, is_max_of_3)

    if Rating.objects.filter(league=game.league, game=game).count() == 0:
        rating1 = Rating(league=game.league, type='game', game=game, datetime=game.end_datetime, player=game.player1,
                         delta=delta, rating_before=r1)
        rating2 = Rating(league=game.league, type='game', game=game, datetime=game.end_datetime, player=game.player2,
                         delta=0 - delta, rating_before=r2)
    else:
        rating1 = Rating.objects.get(league=game.league, game=game, player=game.player1)
        rating2 = Rating.objects.get(league=game.league, game=game, player=game.player2)
        rating1.delta = delta
        rating2.delta = 0 - delta

    rating1.save()
    rating2.save()


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
        cache = caches['league']
        dt_str = self.datetime.strftime("%Y-%m-%d")
        cache_key= u'rating_competitor_list_for_%d_league_%s' % (self.id, dt_str)
        cache.delete(cache_key)

    def __unicode__(self):
        return u"%s (%f) - %s" % (self.player.lastName, self.delta, self.datetime)


@receiver(pre_delete, sender=LeagueCompetitor)
def delete_lc_games(**kwargs):
    instance = kwargs['instance']
    gg = Game.objects.filter(
        league=instance.league
    ).filter(
        Q(player1=instance.competitor)|Q(player2=instance.competitor)
    )
    gg.delete()


class LeagueTournamentSet(models.Model):
    class Meta:
        verbose_name = u'Катерория турнира'
        verbose_name_plural = u'Категории турнира'

    league = models.ForeignKey('League', verbose_name=_(u"Лига"))
    name = models.CharField(verbose_name=_(u"Название"), max_length=255)
    number = models.PositiveSmallIntegerField(verbose_name=_(u"Количество участников"),
                                              null=True, blank=True)


    datetime = models.DateTimeField(
        verbose_name=u'Дата и время турнира',
        blank=True, null=True
    )
    location = models.ForeignKey(
        Location,
        verbose_name=u'Место проведения турнира',
        blank=True, null=True
    )
    is_filled = models.BooleanField(
        verbose_name=u'Данные введены полностью',
        default=False,
    )

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.league.title)

    def get_rating_competitor_list(self):
        league_date = datetime.combine(self.league.end_date, time()) + timedelta(days=3)
        tz = timezone.get_default_timezone()
        league_date = timezone.make_aware(league_date, tz)
        rivals_count = self.league.settings.final_rival_quantity

        rcl = map(lambda x:
                  {
                      'competitor': x.competitor,
                      'rating': x.rating(league_date),
                      'tournament_place': empty2dash(x.tournament_place),
                      'sort_tournament_place': empty2dash(x.tournament_place, get_place),
                      'lc': x,
                      'game_count': x.game_count(league_date),
                      'rival_count': x.rival_count(league_date),
                      'last_game': x.last_game(league_date)
                  }, self.leaguecompetitor_set.all())
        rcl = filter(lambda x: x['rival_count'] >= rivals_count, rcl)
        rcl = sorted(rcl, key=lambda x: x['rating'], reverse=True)
        for i, x in enumerate(rcl):
            if x['tournament_place'] != '-':
                x['place_delta'] = i + 1 - get_place(x['tournament_place'])

        if self.is_filled:
            rcl = sorted(rcl, key=lambda x: x['sort_tournament_place'])

        return rcl


class LeagueCompetitorLeagueChange(models.Model):
    class Meta:
        verbose_name = u'Перемещение между дивизионами'
        verbose_name_plural = u'Перемещения между дивизионами'

    old_league = models.ForeignKey(League, verbose_name=u"Лига (старая)", related_name='old_league_changes')
    new_league = models.ForeignKey(League, verbose_name=u"Лига (новая)", related_name='new_league_changes')
    competitor = models.ForeignKey(Competitor, verbose_name=u"Участник")
    new_rating = models.FloatField(verbose_name=u"Рейтинг в новой лиге")
    created = models.DateTimeField(verbose_name=u"Дата создания", auto_now_add=True)

    def save(self, *args, **kwargs):
        #with transaction.atomic():
        super(LeagueCompetitorLeagueChange, self).save(*args, **kwargs)
        old_lc = LeagueCompetitor.objects.get(league=self.old_league, competitor=self.competitor)
        new_lc, created = LeagueCompetitor.objects_with_moved.get_or_create(league=self.new_league, competitor=self.competitor)
        if not created:
            new_lc.is_moved = False
        rating_before = new_lc.rating()
        rating_delta = self.new_rating - rating_before
        LeagueCompetitor.objects_with_moved.filter(id=old_lc.id).update(is_moved=True)

        if rating_delta != 0:
            Rating.objects.create(league=new_lc.league, type='league_change', datetime=self.created, player=new_lc.competitor,
                       delta=rating_delta, rating_before=rating_before)

    def __unicode__(self):
        return u"%s (%s -> %s)" % (self.competitor, self.old_league.id, self.new_league.id)