from django.contrib.sites.models import Site

from django.utils import timezone


def site(request):
    return {'site': Site.objects.get_current()}


def current_rating_datetime(request):
    return {'current_rating_datetime': timezone.now()}


def kortov_net(request):
    return {'kortov_net': Site.objects.get(id=1)}


def msliga(request):
    return {'msliga': Site.objects.get(id=2)}
