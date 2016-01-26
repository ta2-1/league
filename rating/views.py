# Create your views here.
from django.conf import settings
from django.views.generic.list_detail import object_list, object_detail
from rating.models import Tournament, Competitor, ResultSet, Category, Results, Rule

from league.models import League, Game, get_current_league

from django.template import loader, RequestContext
from django.http import Http404, HttpResponse

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.flatpages.models import FlatPage
 

from utils import get_rating, get_place, get_place_delta, get_place_from_list, get_points_by_params
from livesettings import config_value

def get_evaled_r_place(place, rmc_count, tc_count):
    if place > tc_count:
        return '-'
    return int(round(place * rmc_count / tc_count))
    #return int(eval(config_value('rating', 'R_PLACE')))

def my_get_points_by_params(object, r_place, t_number):
    rmc_count = config_value('rating', 'MAX_COMPETITORS_COUNT')
    rlt_count = config_value('rating', 'LAST_TOURNAMENTS_COUNT')
    
    Y = rmc_count - r_place + 1
    X = rlt_count - t_number + 1
    
    return Y*(Y-1)*rlt_count/2 + X*Y
        
def rules(request, template_name=''):
    rules = Rule.objects.all()
    rmc_count = config_value('rating', 'MAX_COMPETITORS_COUNT')
    places = map(lambda tc_count: map(lambda place: get_evaled_r_place(place, rmc_count, tc_count), range(1, rmc_count+1)), range(1, rmc_count+1))
    rlt_count = config_value('rating', 'LAST_TOURNAMENTS_COUNT')
    points = map(lambda r_place: map(lambda t_number: get_points_by_params(None, r_place, t_number)[1], range(1,rlt_count+1)), range(1,rmc_count+1)) 
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

def index(request, template_name=''):
    cc = []
    for c in Category.objects.filter(show_on_main=True).order_by('position'):
        place_list = c.get_place_list()[:3]
        for p in place_list:
            p['rating_delta'] = int(p['rating']) - int(p['object'].rating_by_category(c.id, 1))  
            p1 = p['object'].place(1)
            p['place_delta'] = (get_place(p1) - get_place(p['place'])) if p1 != '-' else 0
        
        cc.append({'category': c, 'places': place_list})
    
    top = []
    l = None
    last_tournament = None
    last_game_datetime = None

    try:
        l = get_current_league()
        top = l.get_rating_competitor_list()[:16]
        last_game_datetime = Game.objects.all().order_by('-end_datetime')[:1][0].end_datetime
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
        'league': l,
        'top': top,
        'flatpage': f, 
        'last_tournament': last_tournament, 
        'last_game_datetime': last_game_datetime 
    },)
    
    return HttpResponse(t.render(c))

def search(request, template_name=''):
    t = loader.get_template(template_name)
    c = RequestContext(request, {},)
    
    return HttpResponse(t.render(c))

def tournaments(request):
    c = Category.objects.order_by('position')[0]
    
    return redirect(reverse('category', None, (c.id, )))
    
def tournament_list(request):
    return object_list(request, queryset=Tournament.objects.all(), extra_context={'categories': Category.objects.order_by('position')})  

def tournament(request, object_id=''):
    return object_detail(request, queryset=Tournament.objects.all(), object_id=object_id, extra_context={'categories': Category.objects.order_by('position')})

def resultset(request, tournament_id='', category_id=''):
    qrs = ResultSet.objects.filter(tournament__id=tournament_id, category__id=category_id)
    object_id = qrs[0].id 
    
    return object_detail(request, queryset=ResultSet.objects.all(), object_id=object_id, extra_context={'categories': Category.objects.order_by('position')})  

def competitors(request):
    return object_list(request, queryset=Competitor.objects.all())  

def competitor(request, object_id='', template_name = ''):
    l = None
    try:
        l = League.objects.get(id=config_value('league', 'CURRENT_LEAGUE_ID'))
    except:
        pass

    object = Competitor.objects.filter(id=object_id)[0]
    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'object': object,
        'league': l
        #'rating_history': map(lambda x: get_rating(object, object.category.id, x), range(0,15)),   
    },)
    
    return HttpResponse(t.render(c))  

def categories(request):
    return object_list(request, queryset=Category.objects.order_by('position'))
  
def rating(request, category_id = '', template_name = '', tournaments = ''):
    t = loader.get_template(template_name)
    if tournaments == '':
        tournaments = config_value('rating', 'LAST_TOURNAMENTS_COUNT')
    category = Category.objects.filter(id=category_id).get()     
    rs_list = category.get_ordered_resultsets()[0:tournaments]
    
    rating_list = category.get_rating_list_by_results()
    rating_list_1 = category.get_rating_list_by_results(1)
    place_list = category.get_place_dict()
    place_list_1 = category.get_place_dict(1)
    
    competitors = []
    for x in rating_list:
        competitors += [{'object':rating_list[x]['object'],
                         'rating':rating_list[x]['rating'],
                         'rating_delta':rating_list[x]['rating'] - rating_list_1[x]['rating'],
                         'place': get_place_from_list(place_list, rating_list[x]['object'].id),
                         'place_delta':get_place_delta(place_list, place_list_1, rating_list[x]['object'].id),
                         'results': map(lambda z: Results.objects.filter(resultset__id=z.id, competitor__id=rating_list[x]['object'].id, resultset__tournament__is_past=True), rs_list),
                        }]                     
    
    competitors = sorted(filter(lambda z: not(z['rating']==0 and z['object'].category.id !=category.id),competitors), key=lambda x: x['rating'], reverse=True)
    
    c = RequestContext(request, {
        'category': category,
        'result_sets': rs_list,
        'competitors': competitors,
        'categories': Category.objects.order_by('position'),   
    },)
    
    return HttpResponse(t.render(c))
