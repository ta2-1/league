# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time

from django import forms
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatpageForm
from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from modeltranslation.admin import TranslationAdmin

from rating.models import Competitor

from .forms import GameAdminForm
from .models import (
    League, LeagueSettings, LeagueTournament, LeagueTournamentWithSets,
    LeagueCompetitor, Game, Rating, LeagueTournamentSet, LeagueGroup, LeagueCompetitorLeagueChange)
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
    readonly_fields = ('competitor', )
    fields = ('competitor', 'status', 'paid', 'phone')
    extra = 0

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        queryset = super(LeagueCompetitorsInline, self).get_queryset(request)
        return queryset.order_by('competitor__lastName_ru')


class LeagueCompetitorsInlineAdd(admin.TabularInline):
    model = LeagueCompetitor
    fields = ('competitor', 'status', 'paid', 'phone')
    extra = 0

    def has_change_permission(self, request, obj=None):
            return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('competitor'):
            kwargs["queryset"] = Competitor.objects.order_by('lastName_ru')
            return db_field.formfield(**kwargs)

        return super(LeagueCompetitorsInlineAdd, self).formfield_for_foreignkey(db_field, request, **kwargs)
    

class LeagueTournamentCompetitorsInline(admin.TabularInline):
    model = LeagueCompetitor
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ('competitor','saved_rating',)
    fields = ('competitor', 'saved_rating', 'tournament_set', 'tournament_place', 'is_participant')

    class Media:
        js = (
            'league/js/stupidtable.js',
            'league/js/apply_stupidtable.js',
        )
  
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('tournament_set') and hasattr(self, 'league'):
            kwargs["queryset"] = LeagueTournamentSet.objects.filter(league=self.league)
            return db_field.formfield(**kwargs)
        return super(LeagueTournamentCompetitorsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(LeagueTournamentCompetitorsInline, self).get_queryset(request)
        
        if hasattr(self, 'league') and self.league:
            rival_count = self.league.settings.final_rival_quantity
            dt = datetime.combine(self.league.end_date, time())+timedelta(days=2)
            tz = timezone.get_default_timezone()
            dt = timezone.make_aware(dt, tz)
            rcl = self.league.get_rating_competitor_list(dt)
            qs = qs.filter(competitor__id__in=map(lambda x: x['object'].id, filter(lambda x: x['rival_count']>=rival_count, rcl)))

        return qs
    
    def get_formset(self, request, obj=None, **kwargs):
        if isinstance(obj, League):
            self.league = obj

        return super(LeagueTournamentCompetitorsInline, self).get_formset(request, obj, **kwargs)


class LeagueTournamentSetCompetitorsInline(LeagueTournamentCompetitorsInline):
    def get_formset(self, request, obj=None, **kwargs):
        if hasattr(obj, 'league'):
            self.league = obj.league

        return super(LeagueTournamentSetCompetitorsInline, self).get_formset(request, obj, **kwargs)


class LeagueAdmin(LeagueCacheClearTranslationAdmin):
    inlines = (LeagueCompetitorsInline, LeagueCompetitorsInlineAdd)
    list_display = ('title', 'show_add_game_url')

    def show_add_game_url(self, obj):
        return format_html(
            "<a href='{url}'><strong>{add}</strong></a>",
            url=reverse('add_game', kwargs={'league_id': obj.id}),
            add='Add Game'
        )

    show_add_game_url.short_description = _(u"Добавить игру")


class LeagueCompetitorAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'league', 'paid')
    list_filter = ('league', 'paid')
    search_fields = ('competitor__lastName',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('competitor'):
            kwargs["queryset"] = Competitor.objects.order_by('lastName_ru')
            return db_field.formfield(**kwargs)

        return super(LeagueCompetitorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.league.id:
            cache = caches['league']
            cache.delete_where('cache_key > ":1:rating_competitor_list_for_%d_league"' % obj.league.id)
            # cache.delete_where('cache_key LIKE ":1:rating_competitor_list_for_%d_league' % obj.id + '%"')

        obj.save()


class LeagueSettingsAdmin(LeagueSettingsCacheClearTranslationAdmin):
    model = LeagueSettings


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


class LeagueCompetirorLeagueChangeForm(forms.ModelForm):
    competitor = forms.ModelChoiceField(queryset=Competitor.objects.order_by('lastName'))

    class Meta:
        model = LeagueCompetitorLeagueChange
        fields = '__all__'


class LeagueCompetirorLeagueChangeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'new_rating',)
    list_filter = ('old_league', 'new_league')
    search_fields = ('competitor__lastName',)

    form = LeagueCompetirorLeagueChangeForm


class LeagueGroupAdmin(admin.ModelAdmin):
    model = LeagueGroup

class LeagueTournamentSetInline(admin.TabularInline):
    model = LeagueTournamentSet
    extra = 1
    fields = ('name_ru', 'name_en', 'number', 'datetime', 'location')


class LeagueFilledTournamentSetInline(admin.TabularInline):
    model = LeagueTournamentSet
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ('name',)
    fields = ('name', 'is_filled',)


class LeagueTournamentWithSetsAdmin(LeagueCacheClearTranslationAdmin):
    readonly_fields = ('title',)
    fields = ('title',)
    inlines = (LeagueTournamentSetInline, )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LeagueTournamentAdmin(LeagueCacheClearTranslationAdmin):
    readonly_fields = ('title', )
    fields = ('title', )
    inlines = (LeagueFilledTournamentSetInline, LeagueTournamentCompetitorsInline, )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(League, LeagueAdmin)
admin.site.register(LeagueGroup, LeagueGroupAdmin)
admin.site.register(LeagueCompetitor, LeagueCompetitorAdmin)
admin.site.register(LeagueSettings, LeagueSettingsAdmin)
admin.site.register(LeagueTournament, LeagueTournamentAdmin)
admin.site.register(LeagueTournamentWithSets, LeagueTournamentWithSetsAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Rating, RatingAdmin)


class FlatPageAdmin(TranslationAdmin):
    class Media:
        js = ('tiny_mce/tiny_mce.js',
              'tiny_mce/textareas.js',)
    
    form = FlatpageForm

    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        #(_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', )
    search_fields = ('url', 'title')


# We have to unregister it, and then reregister
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
