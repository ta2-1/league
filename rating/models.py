# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rating.utils import get_points, get_place, get_place_from_rating_list
from django.core.cache import cache
from django.db.models import Count


class Rule(models.Model):
    class Meta:
        verbose_name = "Правило"
        verbose_name_plural = "Правила"
        
    text = models.TextField(_(u'Текст правила'), default='')
    
    def __unicode__(self):
        return u"%s" % self.text 
    
class Competitor(models.Model):
    firstName = models.CharField(_(u'Имя'), max_length=250)
    lastName  = models.CharField(_(u'Фамилия'), max_length=250)
    
    birthDate = models.DateField(_(u'Дата рождения'), blank=True, null=True)
    
    categories = models.ManyToManyField('Category', verbose_name=u'Категории', related_name='competitors')
    
    def __unicode__(self):
        return u"%s %s" % (self.lastName, self.firstName)
    
    class Meta:
        verbose_name = _(u'Участник')
        verbose_name_plural = _(u'Участники')
    
    def _get_category(self):
        c = None
        try:
            c = self.categories.all()[0]
        except:
            pass
        return c
    category = property(_get_category)

    def categories(self):
        category_ids = [
            x[0] for x in ResultSet.objects. \
            filter(competitors__id=self.id). \
            values_list('category').distinct()]
        return Category.objects.filter(id__in=category_ids)

    def resultset_points_by_category(self, category, back_offset_number=0):
        cache_key= u'resultset_points_of_competitor_%d_by_category_%d_with_offset_%d' % (self.id, category.id, back_offset_number)
        
        r_points = cache.get(cache_key)
        if r_points is None:     
            rrt_count = category.settings.result_tournaments_count

            r_list = list(
                Results.objects.filter(
                    competitor__id=self.id,
                    resultset__category__id=category.id,
                    resultset__tournament__is_past=True))
            r_points = map(
                lambda x: get_points(
                    x,
                    category.settings.max_competitors_count,
                    category.settings.last_tournaments_count,
                    back_offset_number),
                r_list)
            
            if len(r_points) > rrt_count:
                r_points_sorted = sorted(r_points, key=lambda x: x[1], reverse=True)
            
                for i in range(rrt_count, len(r_points_sorted)):
                    r_points_sorted[i] = (r_points_sorted[i][0], r_points_sorted[i][1], False)
                
                r_points = sorted(r_points_sorted, key=lambda x: x[0].resultset.tournament.start_date)
                cache.set(cache_key, r_points, 60 * 60 * 24 * 30)
        
        return r_points 

    def resultset_points(self):
        res = []
        for category in self.categories():
            res += self.resultset_points_by_category(category)

        return res

    def rating_by_category(self, category, back_offset_number = 0):
        cache_key= u'rating_of_competitor_%d_in_category_%d_with_offset_%d' % (self.id, category.id, back_offset_number)
        
        data = cache.get(cache_key)
        if data is None:
            counted_points = filter(lambda x: x[2], self.resultset_points_by_category(category, back_offset_number))
            counted_points = map(lambda x: x[1], counted_points)
            data = sum(counted_points)
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
        
        return data

    def place_by_category(self, category, back_offset_number = 0):
        cache_key= u'place_of_competitor_%d_in_category_%d' % (self.id, category.id)
        data = cache.get(cache_key)
        if data is None:
            rating_list = category.get_rating_list(back_offset_number)
            for i,x in enumerate(rating_list):
                if x['object'] == self:
                    data = get_place_from_rating_list(rating_list, i)
                                                     
                    break
            else:
                data = None
            
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data
    
    @models.permalink
    def get_absolute_url(self):
        return ('competitor', [], {
            'object_id': self.id,
        })


class CategorySettings(models.Model):
    class Meta:
        verbose_name = u'Параметры расчета рейтинга для категории'
        verbose_name_plural = u'Параметры расчета рейтинга для категории'

    title = models.CharField(
        max_length=255,
        verbose_name=u'Наименование',
    )

    max_competitors_count = models.PositiveIntegerField(
        verbose_name=u'Количество участников',
        help_text = u'Максимальное количество участников в турнире',
        default=32,
    )

    last_tournaments_count = models.PositiveIntegerField(
        verbose_name = u'Количество турниров до обнуления результатов',
        default = 8,
    )

    result_tournaments_count = models.PositiveIntegerField(
        verbose_name = u'Учитываемое количество турниров',
        help_text = u'Результаты скольких последних турниров учитываются при расчете рейтинга участника',
        default = 4
    )

    def __unicode__(self):
        return u"%s" % self.title


class Category(models.Model):
    class Meta:
        verbose_name = _(u'Категория участника')
        verbose_name_plural = _(u'Категории участников')
        ordering = ('position',)
    
    title = models.CharField(_(u'Название'), max_length=25)
    position = models.PositiveSmallIntegerField(_(u'Позиция'))
    show_on_main = models.BooleanField(u'Показывать на главной')
    settings = models.ForeignKey(CategorySettings)

    def __unicode__(self):
        return u"%s" % self.title

    def get_ordered_resultsets(self):
        cache_key= u'ordered_resultsets_for_category_%d' % self.id
        data = cache.get(cache_key)
        if data is None:
            data = list(ResultSet.objects.filter(category__id=self.id,tournament__is_past=True).order_by('-tournament__start_date'))
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data
        
    def get_rating_list(self, back_offset_number = 0):
        cache_key= u'rating_list_only_for_category_%d_with_offset_%d' % (self.id, back_offset_number)
        data = cache.get(cache_key)
        if data is None:
            tdata = map(lambda x: { 'object':x, 'rating':x.rating_by_category(self, back_offset_number) },
                       Competitor.objects.filter(resultsets__category__id=self.id))

            tdata = sorted(tdata, key=lambda x: x['rating'], reverse=True)
            data = []
            for i,x in enumerate(tdata):
                data += [{'object':x['object'], 
                          'rating':x['rating'], 
                          'place':get_place_from_rating_list(tdata, i)
                        }]
                
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data
        
    # добавил для top-16
    def get_place_list(self, back_offset_number = 0):
        cache_key= u'place_list_only_for_category_%d_with_offset_%d' % (self.id, back_offset_number)
        data = cache.get(cache_key)
        
        if data is None:
            data = map(
                lambda x: {
                    'object':x,
                    'rating':x.rating_by_category(self, back_offset_number)
                },
                Competitor.objects.filter(
                    resultsets__category__id=self.id,
                    resultsets__tournament__start_date__gte=self.get_last_tournament_date()
                ).annotate(
                    c=Count('resultsets__id')
                ).filter(c__gte=self.settings.result_tournaments_count))

            data = sorted(data, key=lambda x: x['rating'], reverse=True)
            
            for i,x in enumerate(data):
                x['place'] = get_place_from_rating_list(data, i)
                
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data

    def get_last_tournament_date(self):
        ltc = self.settings.last_tournaments_count
        rss = ResultSet.objects.select_related('tournament') \
            .filter(category=self) \
            .order_by('-tournament__start_date')[:ltc]
        count = rss.count()
        if count < ltc:
            return rss[count - 1].date()
        return rss[ltc - 1].date()

    def get_place_dict(self, back_offset_number = 0):
        cache_key= u'place_dict_only_for_category_%d_with_offset_%d' % (self.id, back_offset_number)
        data = cache.get(cache_key)
        
        if data is None:
            tdata = map(
                lambda x: {
                    'object': x,
                    'rating': x.rating_by_category(self, back_offset_number)},
                Competitor.objects.filter(
                    resultsets__category__id=self.id,
                    resultsets__tournament__start_date__gte=self.get_last_tournament_date()
                ).annotate(
                    c=Count('resultsets__id')
                ).filter(c__gte=self.settings.result_tournaments_count))

            tdata = sorted(tdata, key=lambda x: x['rating'], reverse=True)
            data = {}
            for i, x in enumerate(tdata):
                data = dict(data, **{ x['object'].id: {'place': get_place_from_rating_list(tdata, i), 'rating': x['rating']}})
                
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data

    def get_rating_list_by_results(self, back_offset_number = 0):
        cache_key= u'rating_list_by_results_for_category_%d_with_offset_%d' % (self.id, back_offset_number)
        data = cache.get(cache_key)
        if data is None:
            tdata = map(
                lambda x: {
                    'object':x,
                    'rating':x.rating_by_category(self, back_offset_number)},
                Competitor.objects.filter(
                    results__resultset__category__id=self.id,
                    results__resultset__tournament__is_past=True).distinct())

            tdata = sorted(tdata, key=lambda x: x['rating'], reverse=True)
            data = {}
            for i,x in enumerate(tdata):
                data = dict(data, **{ x['object'].id: {'object': x['object'], 'rating': x['rating']}})
            
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data
    
    
   
class Location(models.Model):
    title = models.CharField(_(u'Название'), max_length=250)
    address = models.CharField(_(u'Адрес'), max_length=250)
    latitude = models.FloatField(_(u'Широта'), blank=True, null=True)
    longitude = models.FloatField(_(u'Долгота'), blank=True, null=True)
    
    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = _(u'Место проведения')
        verbose_name_plural = _(u'Места проведения')
    
class Tournament(models.Model):
    title = models.CharField(_(u'Название'), max_length=250)
    
    start_date = models.DateField(_(u'Дата начала'))
    end_date = models.DateField(_(u'Дата окончания'), blank=True, null=True)
    
    squashclub_url = models.CharField(_(u'Ссылка на турнир на squashclub.ru'), max_length=200, blank=True)
    is_past = models.BooleanField(_(u'Турнир прошел (учитывать при подсчете рейтинга)')) 
    
    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = _(u'Турнир')
        verbose_name_plural = _(u'Турниры')
        
    @models.permalink
    def get_absolute_url(self):
        return ('tournament', [], {
            'object_id': self.id,
        })
        
    def get_date(self):
        from django.template.context import Context
        from django.template.base import Template
        
        if self.start_date == self.end_date:
            t = Template('{{date|date:"j E Y"}}')
            c = Context({'date': self.start_date})
            return t.render(c)
        else:
            t = Template('{{date|date:"E Y"}}')
            c = Context({'date': self.start_date})
            return u"с %d по %d %s" % (self.start_date.day, self.end_date.day, t.render(c))
            
        
                              
class ResultSet(models.Model):
    tournament = models.ForeignKey('Tournament', verbose_name=u'Турнир')
    category = models.ForeignKey('Category', verbose_name=u'Категория')
    competitors = models.ManyToManyField('Competitor', through='Results', related_name='resultsets')
    locations = models.ManyToManyField('Location', related_name="resultsets", verbose_name=u'Места проведения')     
    
    class Meta:
        verbose_name = _(u'Сетка результатов')
        verbose_name_plural = _(u'Сетки результатов')
        
    def date(self):
        return self.tournament.start_date
    
    def sequence_number(self):  
        cache_key= u'sequence_number_for_resultset_%d' % self.id
        data = cache.get(cache_key)
        if data is None:
            rs_list = self.category.get_ordered_resultsets()
            data = rs_list.index(self)+1
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data
        
    def locations__set(self):
        return Location.objects.filter(resultsets__id=self.id)
    
    def competitors_count(self):
        cache_key= u'competitors_count_for_resultset_%d' % self.id
        data = cache.get(cache_key)
        
        if data is None:
            data = Results.objects.filter(resultset__id=self.id).aggregate(Count('competitor'))
            cache.set(cache_key, data, 60 * 60 * 24 * 30)
            
        return data['competitor__count']  
           
    def __unicode__(self):
        return u'<a href="/admin/rating/resultset/%d"> Сетка по категории %s</a>' % (self.id, self.category.title)

class Results(models.Model):
    competitor = models.ForeignKey('Competitor', verbose_name=u'Участник')
    resultset = models.ForeignKey('ResultSet', verbose_name=u'Сетка результатов')
    place = models.CharField(_(u'Место'), max_length=10)
    
    class Meta:
        verbose_name = _(u'Результат')
        verbose_name_plural = _(u'Результаты')
    
    def rplace(self):
        return get_place(self.place)
    
    def points(self):
        p = get_points(
            self,
            self.resultset.category.settings.max_competitors_count,
            self.resultset.category.settings.last_tournaments_count)
        return p[1]
    

    #def __unicode__(self):
    #    return u"%s: %s  (%s)" %  (str(self.resultset.tournament), str(self.competitor), str(self.place))
