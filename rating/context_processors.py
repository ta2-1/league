from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from partners.models import Partner

def site(request):
    return {'site': get_current_site(request)}


def kortov_net(request):
    return {'kortov_net': Site.objects.get(domain='kortov.net')}


def msliga(request):
    return {'msliga': Site.objects.get(domain='msliga.ru')}


def partners(request):
    return {'partners': Partner.objects.all()}
