# -*- coding: utf-8 -*-

from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from partners.models import Partner


admin.site.register(Partner, TranslationAdmin)
