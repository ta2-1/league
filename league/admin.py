# -*- coding: utf-8 -*-
from django.contrib import admin

from rating.models import Competitor  
from league.models import get_current_league, League, LeagueSettings, LeagueTournament, LeagueAlterTournament, LeagueCompetitor, Game, Rating

from league.forms import GameAdminForm
from django.core.cache import get_cache 

from modeltranslation.admin import TranslationAdmin

from datetime import datetime, timedelta, time

class LeagueCacheClearTranslationAdmin(TranslationAdmin):
    def save_model(self, request, obj, form, change):
        if obj.id:
            cache = get_cache('league')
            cache.delete_where('cache_key > ":1:rating_competitor_list_for_%d_league"' % obj.id)
            #cache.delete_where('cache_key LIKE ":1:rating_competitor_list_for_%d_league' % obj.id + '%"')
        
        obj.save()

class LeagueSettingsCacheClearTranslationAdmin(TranslationAdmin):
    def save_model(self, request, obj, form, change):
        for l in  obj.league_set.all():
            cache = get_cache('league')
            #cache.delete_where('cache_key > ":1:rating_competitor_list_for_%d_league"' % l.id)
            #cache.delete_where('cache_key LIKE ":1:rating_competitor_list_for_%d_league' % obj.id + '%"')
        
        obj.save()

class GameCacheClearAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        cache = get_cache('league')
        cache.delete_where('cache_key >= ":1:rating_competitor_list_for_%d_league_%s"' % (obj.league.id, obj.end_datetime.strftime("%Y-%m-%d")))
        
        obj.save()

class RatingCacheClearAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        cache = get_cache('league')
        cache.delete_where('cache_key >= ":1:rating_competitor_list_for_%d_league_%s"' % (obj.league.id, obj.datetime.strftime("%Y-%m-%d")))
        
        obj.save()

class LeagueCompetitorsInline(admin.TabularInline):
    model = LeagueCompetitor
    fields = ('competitor', 'status', 'paid')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('competitor'):
            kwargs["queryset"] = Competitor.objects.order_by('lastName_ru')
            return db_field.formfield(**kwargs)
        
        return super(LeagueCompetitorsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
class LeagueTournamentCompetitorsInline(admin.TabularInline):
    model = LeagueCompetitor
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ('competitor','saved_rating',)
    fields = ('competitor', 'saved_rating', 'tournament_place', 'tournament_category', 'is_participant')
    #ordering = ('saved_rating',)
    
    class Media:
        js = (
            'league/js/stupidtable.js',
            'league/js/apply_stupidtable.js',
        )
  
    def queryset(self, request):
        qs = super(LeagueTournamentCompetitorsInline, self).queryset(request)
        
        if hasattr(self, 'league') and self.league:
            rcl = self.league.get_rating_competitor_list(datetime.combine(self.league.end_date, time())+timedelta(days=2))
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=10, rcl)))
        
        return qs
    
    def get_formset(self, request, obj=None, **kwargs):
        self.league = obj

        return super(LeagueTournamentCompetitorsInline, self).get_formset(request, obj, **kwargs)

class LeagueTournamentACompetitorsInline(LeagueTournamentCompetitorsInline):
    model = LeagueCompetitor

    def queryset(self, request):
        qs = super(LeagueTournamentCompetitorsInline, self).queryset(request)
        if hasattr(self, 'league') and self.league:
            rcl = self.league.get_rating_competitor_list(datetime.combine(self.league.end_date, time())+timedelta(days=2))
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=10, rcl)[:16]))
        return qs

class LeagueTournamentBCompetitorsInline(LeagueTournamentCompetitorsInline):
    model = LeagueCompetitor

    def queryset(self, request):
        qs = super(LeagueTournamentBCompetitorsInline, self).queryset(request)
        if hasattr(self, 'league') and self.league:
            rcl = self.league.get_rating_competitor_list(datetime.combine(self.league.end_date, time())+timedelta(days=2))
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=10, rcl)[16:]))
        return qs

class LeagueAdmin(LeagueCacheClearTranslationAdmin):
    exclude = ('tournament_a_datetime', 'tournament_b_datetime', 'location', 'is_tournament_data_filled')
    inlines = (LeagueCompetitorsInline,)

class LeagueSettingsAdmin(LeagueSettingsCacheClearTranslationAdmin):
    model = LeagueSettings

class LeagueTournamentAdmin(LeagueCacheClearTranslationAdmin):
    inlines = (LeagueTournamentACompetitorsInline, LeagueTournamentBCompetitorsInline)
    fields = ('tournament_a_datetime', 'tournament_b_datetime', 'location', 'is_tournament_data_filled')
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class LeagueTournamentAlterAdmin(LeagueCacheClearTranslationAdmin):
    inlines = (LeagueTournamentCompetitorsInline, )
    fields = ('tournament_a_datetime', 'tournament_b_datetime', 'location', 'is_tournament_data_filled')
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class GameAdmin(GameCacheClearAdmin):
    class Media:
        js = ('league/js/add_game.js',)
    
    add_form_template='league/admin/add_game.html'
    fieldsets = (
        (None, {
            'fields': ('league', ('start_datetime', 'end_datetime'), 'no_record', 'player1', 'player2', 'location', ('result1', 'result2'))
        }),
    )
        
    form = GameAdminForm
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        league = get_current_league()
        if db_field.name == 'league':
            kwargs['initial'] = league
            return db_field.formfield(**kwargs)

        if db_field.name in ('player1','player2'):
            kwargs["queryset"] = Competitor.objects.filter(leaguecompetitor__league=league).order_by('lastName')
            return db_field.formfield(**kwargs)
        
        return super(GameAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class RatingAdmin(RatingCacheClearAdmin):
    list_display = ('__unicode__', 'game',)

admin.site.register(League, LeagueAdmin)
admin.site.register(LeagueSettings, LeagueSettingsAdmin)
admin.site.register(LeagueTournament, LeagueTournamentAdmin)
admin.site.register(LeagueAlterTournament, LeagueTournamentAlterAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Rating, RatingAdmin)


from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatpageForm 
from django.utils.translation import ugettext_lazy as _

class FlatPageAdmin(TranslationAdmin):
    class Media:
        js = ('tiny_mce/tiny_mce.js',
              'tiny_mce/textareas.js',)
    
    form = FlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')


# We have to unregister it, and then reregister
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
