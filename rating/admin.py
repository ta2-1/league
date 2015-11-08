# -*- coding: utf-8 -*-
from django.contrib import admin
from rating.models import *
from django.core.cache import cache

from modeltranslation.admin import TranslationAdmin


class CacheClearTranslationAdmin(TranslationAdmin):
    def save_model(self, request, obj, form, change):
        cache.clear()
        obj.save()

class CacheClearAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        cache.clear()
        obj.save()

class CompetitorAdmin(CacheClearTranslationAdmin):
    list_display = ['id', 'lastName_ru', 'firstName_ru','lastName_en', 'firstName_en']
    search_fields = ['lastName_ru', 'firstName_ru', 'lastName_en', 'firstName_en']
    list_editable = ['lastName_ru', 'firstName_ru', 'lastName_en', 'firstName_en']

    
class CategoryAdmin(CacheClearTranslationAdmin):
    list_display = ['title', 'position']
    list_editable = ['position']
    
    class Media:
        js = (
            'admin/js/admin-list-reorder.js',
        )    

class LocationAdmin(CacheClearTranslationAdmin):
    list_display = ['title', 'address']
    
class RuleAdmin(CacheClearTranslationAdmin):
    list_display = ['text', ]
    
class ResultSetInline(admin.TabularInline):
    model = ResultSet
    #filter_horisontal = ('locations', )
    

class TournamentAdmin(CacheClearTranslationAdmin):
    list_display = ['title', 'start_date', 'end_date', 'squashclub_url']
    inlines = (ResultSetInline,)
    
    
class ResultsInline(admin.TabularInline):
    model = Results
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('competitor'):
            kwargs["queryset"] = Competitor.objects.order_by('lastName_ru')
            return db_field.formfield(**kwargs)
 
class ResultSetAdmin(CacheClearAdmin):
    list_display = ['tournament', 'category', 'date']
    inlines = (ResultsInline,)
    
    
#class TournamentResultsAdmin(admin.ModelAdmin):
#    readonly_fields  = ['title', 'date', 'location']


#class ResultsAdmin(admin.ModelAdmin):
#    list_display = ['competitor', 'tournament', 'place']

admin.site.register(Competitor, CompetitorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(ResultSet, ResultSetAdmin)
admin.site.register(Rule, RuleAdmin)
