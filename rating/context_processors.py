from django.contrib.sites.models import Site

from datetime import datetime
from league.utils import get_league_rating_datetime

def site(request):
    return { 'site': Site.objects.get_current() }


def current_rating_datetime(request):
    return { 'current_rating_datetime': get_league_rating_datetime(datetime.now()) }
