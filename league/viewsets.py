from django.http import HttpResponseBadRequest
from django.utils import timezone

from rest_framework import serializers, viewsets, response
from rest_framework.decorators import detail_route

from rating.models import Competitor, Location

from league.models import League, Game, get_current_leagues


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
