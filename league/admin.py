# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time

from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatpageForm
from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from modeltranslation.admin import TranslationAdmin

from rating.models import Competitor

from .forms import GameAdminForm
from .models import (get_current_leagues, League, LeagueSettings, LeagueTournament,
                           LeagueAlterTournament, LeagueCompetitor, Game, Rating)
from .utils import clear_cache_on_game_save


class LeagueCacheClearTranslationAdmin(TranslationAdmin):
    def save_model(self, request, obj, form, change):
        if obj.id:
            cache = caches['league']
            cache.delete_where('cache_key > ":1:rating_competitor_list_for_%d_league"' % obj.id)
            #cache.delete_where('cache_key LIKE ":1:rating_competitor_list_for_%d_league' % obj.id + '%"')
        
        obj.save()


class LeagueSettingsCacheClearTranslationAdmin(TranslationAdmin):
    def save_model(self, request, obj, form, change):
        for l in obj.league_set.all():
            cache = caches['league']
            #cache.delete_where('cache_key > ":1:rating_competitor_list_for_%d_league"' % l.id)
            #cache.delete_where('cache_key LIKE ":1:rating_competitor_list_for_%d_league' % obj.id + '%"')
        
        obj.save()


class GameCacheClearAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        clear_cache_on_game_save(obj)
        obj.save()


class RatingCacheClearAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        cache = caches['league']
        league_prefix = ":1:rating_competitor_list_for_%d_league" % \
                        obj.league.id
        where = ("cache_key LIKE '%(league_prefix)s%%' AND "
                "cache_key >= '%(league_prefix)s_%(datetime)s'" %
                {'league_prefix': league_prefix,
                 'datetime': obj.datetime.strftime("%Y-%m-%d")})
        cache.delete_where(where)
        
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

    class Media:
        js = (
            'league/js/stupidtable.js',
            'league/js/apply_stupidtable.js',
        )
  
    def get_queryset(self, request):
        qs = super(LeagueTournamentCompetitorsInline, self).get_queryset(request)
        
        if hasattr(self, 'league') and self.league:
            rival_count = self.league.settings.final_rival_quantity
            rcl = self.league.get_rating_competitor_list(datetime.combine(self.league.end_date, time())+timedelta(days=2))
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=rival_count, rcl)))

        return qs
    
    def get_formset(self, request, obj=None, **kwargs):
        self.league = obj

        return super(LeagueTournamentCompetitorsInline, self).get_formset(request, obj, **kwargs)


class LeagueTournamentACompetitorsInline(LeagueTournamentCompetitorsInline):
    model = LeagueCompetitor

    def get_queryset(self, request):
        qs = super(LeagueTournamentCompetitorsInline, self).get_queryset(request)
        if hasattr(self, 'league') and self.league:
            rival_count = self.league.settings.final_rival_quantity
            rcl = self.league.get_rating_competitor_list(datetime.combine(self.league.end_date, time())+timedelta(days=2))
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=rival_count, rcl)[:16]))
        return qs


class LeagueTournamentBCompetitorsInline(LeagueTournamentCompetitorsInline):
    model = LeagueCompetitor

    def get_queryset(self, request):
        qs = super(LeagueTournamentBCompetitorsInline, self).get_queryset(request)
        if hasattr(self, 'league') and self.league:
            rival_count = self.league.settings.final_rival_quantity
            rcl = self.league.get_rating_competitor_list(datetime.combine(self.league.end_date, time())+timedelta(days=2))
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=rival_count, rcl)[16:]))
        return qs


class LeagueAdmin(LeagueCacheClearTranslationAdmin):
    exclude = ('tournament_a_datetime', 'tournament_b_datetime', 'location', 'is_tournament_data_filled')
    inlines = (LeagueCompetitorsInline,)
    list_display = ('title', 'show_add_game_url')

    def show_add_game_url(self, obj):
        return format_html(
            "<a href='{url}'><strong>{add}</strong></a>",
            url=reverse('add_game', kwargs={'league_id': obj.id}),
            add='Add Game'
        )

    show_add_game_url.short_description = ""


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
    list_filter = ('added_via_api', 'league', 'location', 'end_datetime')
    search_fields = ('player1__lastName', 'player2__lastName',)
    form = GameAdminForm

    def __init__(self, *args, **kwargs):
        if 'league' in kwargs:
            self.league = kwargs.pop('league')
        return super(GameAdmin, self).__init__(*args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('player1', 'player2') and hasattr(self, 'league'):
            kwargs["queryset"] = Competitor.objects.filter(
                leaguecompetitor__league=self.league
            ).order_by('lastName')
            return db_field.formfield(**kwargs)
        return super(GameAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(GameAdmin, self).get_form(request, obj, **kwargs)

        if obj is not None:
            form.base_fields['player1'].queryset = Competitor.objects.filter(id=obj.player1_id).order_by('lastName')
            form.base_fields['player2'].queryset = Competitor.objects.filter(id=obj.player2_id).order_by('lastName')
            form.base_fields['player2'].widget.widget.attrs['disabled'] = 'disabled'
            form.base_fields['player1'].widget.widget.attrs['disabled'] = 'disabled'
        elif hasattr(self, 'league'):
            form.base_fields['league'].initial = self.league

        return form

    def has_add_permission(self, request):
        return hasattr(self, 'league')


class RatingAdmin(RatingCacheClearAdmin):
    list_display = ('__unicode__', 'game',)
    list_filter = ('league', 'game__location', 'datetime')
    search_fields = ('player__lastName',)


admin.site.register(League, LeagueAdmin)
admin.site.register(LeagueSettings, LeagueSettingsAdmin)
admin.site.register(LeagueTournament, LeagueTournamentAdmin)
admin.site.register(LeagueAlterTournament, LeagueTournamentAlterAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Rating, RatingAdmin)


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
