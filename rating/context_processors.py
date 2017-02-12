from django.contrib.sites.models import Site

from datetime import datetime

from django.utils import timezone


def site(request):
    return {'site': Site.objects.get_current()}


def current_rating_datetime(request):
    return {'current_rating_datetime': timezone.now()}
