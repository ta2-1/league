#import os
#import gettext as gettext_module

from django import http
from django.http import HttpResponse
from django.conf import settings
#from django.utils import importlib
from django.utils.translation import check_for_language, activate, get_language
#, to_locale, get_language
#from django.utils.text import javascript_quote
#from django.utils.encoding import smart_unicode
#from django.utils.formats import get_format_modules, get_format

def set_language(request):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'GET' or request.method == 'POST':
        lang_code = request.GET.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            activate(lang_code)
    #return HttpResponse("code = %s, django lang = %s, current = %s" % (lang_code, request.session['django_language'], get_language()))
    return response
