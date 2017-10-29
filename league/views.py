import json

from datetime import datetime, time, timedelta

from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.template import loader, RequestContext
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from rest_framework import serializers, viewsets, response
from rest_framework.decorators import detail_route

from rating.models import Competitor, Location
from rating.genericviews import (
    DetailedWithExtraContext as DetailView,
    ListViewWithExtraContext as ListView)

from league.models import get_current_leagues, Game, League, LeagueCompetitor, Rating
from league.utils import (
    league_get_N, league_get_DELTA, get_league_rating_datetime,
    get_rating_competitor_list)


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        #model = User
        fields = ('url', 'id', 'username', 'name', 'phone', 'email',
                  'balance', 'booked', 'multiplier', 'price_level',
                  'default_price_level')

    @property
    def data(self):
        if hasattr(self, '_data'):
            del self._data
        return super(UserSerializer, self).data


class LeagueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = League
        fields = ('id', 'title', 'start_date', 'end_date')


class LeagueCompetitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Competitor
        fields = ('id', 'first_name', 'last_name')


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

    def get_queryset(self):
        queryset = League.objects.filter(id__in=map(lambda x: x.id, get_current_leagues()))

        return queryset

    @detail_route()
    def players(self, request, *args, **kwargs):
        league = self.get_object()
        competitors = Competitor.objects.filter(leaguecompetitor__league=league)

        return response.Response(LeagueCompetitorSerializer(competitors, many=True).data)


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'title', 'address', 'latitude', 'longitude')


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class GameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'player1', 'player2', 'result1', 'result2', 'end_datetime',
                  'rating_delta', 'location', 'league')

    player1 = serializers.PrimaryKeyRelatedField(queryset=Competitor.objects.all().order_by('lastName'))
    player2 = serializers.PrimaryKeyRelatedField(queryset=Competitor.objects.all().order_by('lastName'))
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all())
    end_datetime = serializers.DateTimeField(default_timezone=timezone.get_default_timezone())

    def save(self, **kwargs):
        return super(GameSerializer, self).save(added_via_api=True, **kwargs)


class GameViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super(GameViewSet, self).create(request, *args, **kwargs)
        except:
            return HttpResponseBadRequest()


class LeaguesView(TemplateView):
    template_name = 'league/current_leagues.html'

    def get_context_data(self, **kwargs):
        ll = get_current_leagues()
        dt = timezone.now().replace(hour=0, minute=0, second=0)
        ctx = {'leagues': []}

        for l in ll:
            if not l.visible:
                continue
            if not l.is_ended() or not l.is_tournament_data_filled:
                ctx['leagues'].append(get_league_rating_context(l, dt))
            else:
                ctx['leagues'].append(get_league_result_context(l))

        return ctx


@never_cache
def league_list(request, template_name):
    return ListView.as_view(
        queryset=League.objects.filter(visible=True),
        template_name=template_name
    )(request)


def get_league_rating_context(league, dt):
    rcl = league.get_rating_competitor_list(dt)
    return {
        'league': league,
        'rcl': rcl,
        'league_rating_datetime': dt
    }


class LeagueDetailView(DetailView):
    model = League
    pk_url_kwarg = 'league_id'


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


class LeagueStatementView(LeagueDetailView):
    template_name = 'league/statement.html'

    def get_context_data(self, **kwargs):
        f = get_object_or_404(FlatPage, id=self.object.statement_id)
        return {'flatpage': f, 'league': self.object}


class LeagueRulesView(LeagueDetailView):
    template_name = 'league/rules.html'
    def get_context_data(self, **kwargs):
        f = get_object_or_404(FlatPage, id=self.object.rules_id)
        return {'flatpage': f, 'league': self.object}


class LeagueRatingView(LeagueDetailView):
    template_name = 'league/rating.html'

    def get_context_data(self, **kwargs):
        try:
            if self.request.GET.has_key('date'):
                date = datetime.strptime(self.request.GET['date'], '%d.%m.%Y')

                dt = date.replace(hour=0, minute=0, second=0)
                dt = timezone.make_aware(dt, timezone.get_default_timezone())
            else:
                dt = timezone.now()
        except:
            dt = timezone.now()

        league = self.get_object()

        return get_league_rating_context(league, league.current_rating_datetime)


class LeagueResultsView(LeagueDetailView):
    template_name = 'league/results.html'

    def get(self, request, *args, **kwargs):
        league = self.get_object()
        if league.is_ended():
            return super(LeagueResultsView, self).get(request, *args, **kwargs)
        else:
            return redirect('/leagues/%s' % league.id)


class LeagueGamesView(LeagueDetailView):
    template_name = 'league/games.html'

    def get_context_data(self, **kwargs):
        games = (
            Game.objects.filter(league=self.get_object())
                        .select_related('location', 'player1',
                                        'player2', 'league')
                        .order_by('-end_datetime'))
        num = 0
        for game in games:
            if not game.no_record:
                num += 1
                game.number = num
        for game in games:
            if hasattr(game, 'number'):
                game.number = num - game.number + 1

        return {
            'league': self.get_object(),
            'object_list': games,
        }


class LeaguePenaltiesView(LeagueDetailView):
    template_name = 'league/penalties.html'

    def get_context_data(self, **kwargs):

        rr = Rating.objects.filter(
            league=self.get_object(),
            type='penalty'
        ).select_related('league', 'player').order_by('datetime')

        return {
            'league': self.get_object(),
            'object_list': rr,
        }


@never_cache
def competitor(request, league_id, competitor_id, template_name):
    leaguecompetitors = LeagueCompetitor.objects.filter(league__visible=True, competitor__id=competitor_id) \
                                        .select_related('league', 'competitor') \
                                        .order_by('league__start_date')
    try:
        leaguecompetitor = LeagueCompetitor.objects.select_related('league', 'competitor') \
                                           .get(league__id=league_id, competitor__id=competitor_id)
    except LeagueCompetitor.DoesNotExist:
        raise Http404('No %s matches the given query.' % LeagueCompetitor._meta.object_name)

    i = 1
    rr = list(Rating.objects.filter(player__id=competitor_id, league__id=league_id)
                            .select_related('player', 'league', 'game', 'game__player1',
                                            'game__player2', 'game__league')
                            .order_by('datetime')
    )
    for r in rr:
        r.number = i
        if r.type == 'game' and r.game and not r.game.no_record:
            i += 1
    rr = list(reversed(rr))

    # add penalties
    #rr = Rating.objects.filter(player__id=competitor_id, type='game', league__id=league_id).order_by('-datetime')

    #games = Game.objects.filter(Q(player1__id=competitor_id)|Q(player2__id=competitor_id), league__id=league_id).order_by('-end_datetime')
    #r_games = map(lambda x: {'game': x, 'delta': leaguecompetitor.get_delta_rating(x)}, games)
    extra_context={'rr': rr, 'leaguecompetitors': leaguecompetitors, 'leaguecompetitor': leaguecompetitor}

    return DetailView.as_view(
        queryset=Competitor.objects.all(),
        template_name=template_name
    )(
        request,
        pk=competitor_id,
        extra_context=extra_context
    )

@never_cache
def competitor_leagues(request, competitor_id):
    league_id = get_current_leagues()[0].id
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

    return DetailView.as_view(
        queryset=Competitor.objects.all(),
        template_name=template_name
    )(
        request,
        pk=competitor_id,
        extra_context={'leaguecompetitors': leaguecompetitors}
    )

@never_cache
def competitors_vs(request, competitor1_id, competitor2_id, template_name):
    games = Game.objects.filter(Q(player1__id=competitor1_id, player2__id=competitor2_id)|Q(player1__id=competitor2_id, player2__id=competitor1_id), league__visible=True).order_by('-end_datetime')

    return DetailView.as_view(
        queryset=Competitor.objects.all(),
        template_name=template_name
    )(
        request,
        pk=competitor1_id,
        extra_context={
            'opponent': get_object_or_404(Competitor, id=competitor2_id),
            'games': games
        }
    )

@never_cache
def competitor_rivals(request, competitor_id, template_name):
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

    return DetailView.as_view(
        queryset=Competitor.objects.all(),
        template_name=template_name
    )(
        request,
        pk=competitor_id,
        extra_context={'rivals': rivals}
    )


def get_possible_opponents(lc, dt=None):
    if dt is None:
        dt = get_league_rating_datetime(timezone.now())
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
    live_rcl = lc.league.get_rating_competitor_list(timezone.now()+timedelta(days=2))
    dt = timezone.now().replace(hour=0, minute=0, second=0)
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

    return DetailView.as_view(
        queryset=Competitor.objects.all(),
        template_name=template_name
    )(
        request,
        pk=competitor_id,
        extra_context={'rivals': rivals, 'lc': lc}
    )


@never_cache
def competitor_opponents(request, league_id, competitor_id):
    lc = get_object_or_404(LeagueCompetitor, league__id=league_id, competitor__id=competitor_id)
    #lc = LeagueCompetitor.objects.get(league__id=league_id, competitor__id=competitor_id)
    #json_data = json.dumps(map(lambda x: x['object'].id, lc.get_possible_opponents()))

    try:
        if request.GET.has_key('date'):
            date = datetime.strptime(request.GET['date'], '%d.%m.%Y')
            dt = date.replace(hour=0, minute=0, second=0)
        else:
            dt = None
    except:
        dt = None

    ol = list(Competitor.objects.filter(
        leaguecompetitor__league=lc.league
    ).exclude(
        leaguecompetitor__id=lc.id
    ).order_by(
        'lastName',
        'firstName'
    ).values('id', 'firstName', 'lastName'))
    for x in ol:
        x.update(
            {
                'name': u"%s %s" % (
                    x['lastName'],
                    x['firstName'],
                )
            }
        )

    json_data = json.dumps({'HTTPRESPONSE':1, 'data': ol}, ensure_ascii=False)

    return HttpResponse(json_data, content_type="application/json")


def add_game(request, league_id):
    from admin import GameAdmin
    from django.contrib import admin

    league = League.objects.get(id=league_id)
    if request.method == 'POST':
        request.POST['league'] = league_id
    return GameAdmin(Game, admin.site, league=league).add_view(request)
