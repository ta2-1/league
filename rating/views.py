# Create your views here.
from django.conf import settings
from rating.models import Tournament, Competitor, ResultSet, Category, Results, Rule, CategorySettings

from league.models import Game, get_current_leagues

from django.template import loader, RequestContext
from django.http import HttpResponse

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.flatpages.models import FlatPage
from django.views.decorators.cache import cache_page

from utils import get_place, get_place_delta, get_place_from_list, get_points_by_params
from genericviews import DetailedWithExtraContext as DetailView, ListViewWithExtraContext as ListView


def get_evaled_r_place(place, rmc_count, tc_count):
    if place > tc_count:
        return '-'
    return int(round(place * rmc_count / tc_count))


@cache_page(60*60*24*7)
def rules(request, template_name=''):
    rules = Rule.objects.all()
    cs = CategorySettings.objects.get(id=1)
    rmc_count = cs.max_competitors_count
    places = map(
        lambda tc_count: map(
            lambda place: get_evaled_r_place(place, rmc_count, tc_count),
            range(1, rmc_count+1)),
        range(1, rmc_count+1))
    rlt_count = cs.last_tournaments_count
    points = map(
        lambda r_place: map(
            lambda t_number: get_points_by_params(None, r_place, t_number, rmc_count, rlt_count)[1],
            range(1,rlt_count+1)),
        range(1,rmc_count+1))
    for pp in points:
        pp.reverse()

    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'rules': rules,
        'place_numbers': range(1,rmc_count+1),
        'places': places,
        'tournament_numbers': map(lambda x: rlt_count - x + 1, range(1,rlt_count+1)),
        'points': points,
        'categories': Category.objects.order_by('position'),   
    },)
    
    return HttpResponse(t.render(c))  


@cache_page
def index(request, template_name=''):
    cc = []
    for c in Category.objects.filter(show_on_main=True).order_by('position'):
        try:
            place_list = c.get_place_list()[:3]
            for p in place_list:
                p['rating_delta'] = int(p['rating']) - int(p['object'].rating_by_category(c, 1))
                p1 = p['object'].place_by_category(c, 1)
                p['place_delta'] = (get_place(p1) - get_place(p['place'])) if p1 != '-' else 0

            cc.append({'category': c, 'places': place_list})
        except IndexError:
            pass

    last_tournament = None
    current_leagues = []
    try:
        ll = get_current_leagues()
        for l in ll:
            item = {'league': l}
            item['top'] = l.get_rating_competitor_list()[:16]
            current_leagues.append(item)
    except:
        pass

    try:
        last_tournament = Tournament.objects.all().order_by('-end_date')[:1][0]
    except:
        pass

    url = request.path_info
    if not url.startswith('/'):
        url = "/" + url

    f = get_object_or_404(FlatPage, url__exact=url, sites__id__exact=settings.SITE_ID)

    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'categories': cc,
        'current_leagues': current_leagues,
        'flatpage': f,
        'last_tournament': last_tournament,
    },)

    return HttpResponse(t.render(c))


def search(request, template_name=''):
    t = loader.get_template(template_name)
    c = RequestContext(request, {},)
    
    return HttpResponse(t.render(c))

@cache_page(60*60*24*7)
def tournaments(request):
    c = Category.objects.order_by('position')[0]
    
    return redirect(reverse('category', None, (c.id, )))

@cache_page(60*60*24*7)
def tournament_list(request):
    return ListView.as_view(queryset=Tournament.objects.all())(request, extra_context={'categories': Category.objects.order_by('position')})


@cache_page(60*60*24*7)
def tournament(request, object_id=''):
    return DetailView.as_view(queryset=Tournament.objects.all())(request, pk=object_id, extra_context={'categories': Category.objects.order_by('position')})


@cache_page(60*60*24*7)
def resultset(request, tournament_id='', category_id=''):
    qrs = ResultSet.objects.filter(tournament__id=tournament_id, category__id=category_id)
    object_id = qrs[0].id 
    
    return DetailView.as_view(queryset=ResultSet.objects.all())(request, pk=object_id, extra_context={'categories': Category.objects.order_by('position')})


@cache_page(60*60*24*7)
def competitors(request):
    return ListView().as_view(queryset=Competitor.objects.all())(request)


@cache_page(60*60*24*7)
def competitor(request, object_id='', template_name = ''):
    from league.models import get_current_leagues
    ll = get_current_leagues()
    l = ll[0] if len(ll) > 0 else None

    object = Competitor.objects.filter(id=object_id)[0]
    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'object': object,
        'object_categories': [
            (c,
             object.place_by_category(c),
             object.rating_by_category(c)) for c in object.categories()],
        'league': l
    },)
    
    return HttpResponse(t.render(c))  


@cache_page(60*60*24*7)
def categories(request):
    return ListView.as_view(queryset=Category.objects.order_by('position'))(request)
  

@cache_page(60*60*24*7)
def rating(request, category_id='', template_name='', tournaments=''):
    t = loader.get_template(template_name)
    category = Category.objects.get(id=category_id)
    if tournaments == '':
        tournaments = category.settings.last_tournaments_count

    rs_list = category.get_ordered_resultsets()[0:tournaments]
    
    rating_list = category.get_rating_list_by_results()
    rating_list_1 = category.get_rating_list_by_results(1)
    place_list = category.get_place_dict()
    place_list_1 = category.get_place_dict(1)
    
    competitors = []
    for x in rating_list:
        competitors += [
            {'object':rating_list[x]['object'],
             'rating':rating_list[x]['rating'],
             'rating_delta':rating_list[x]['rating'] - rating_list_1[x]['rating'],
             'place': get_place_from_list(place_list, rating_list[x]['object'].id),
             'place_delta':get_place_delta(
                 place_list,
                 place_list_1,
                 rating_list[x]['object'].id),
            'results': map(
                lambda z: Results.objects.select_related(
                    'resultset__category__categorysettings').
                    filter(
                        resultset__id=z.id,
                        competitor__id=rating_list[x]['object'].id,
                        resultset__tournament__is_past=True),
                rs_list), }]

    competitors = sorted(filter(lambda z: not z['rating'] == 0, competitors), key=lambda x: x['rating'], reverse=True)
    
    c = RequestContext(request, {
        'category': category,
        'result_sets': rs_list,
        'competitors': competitors,
        'categories': Category.objects.order_by('position'),   
    },)
    
    return HttpResponse(t.render(c))
