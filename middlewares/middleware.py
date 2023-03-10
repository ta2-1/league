from django.conf import settings


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers
    
    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies
    
    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
            del request.META['HTTP_ACCEPT_LANGUAGE']


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """
    if not request.user.is_superuser:
        return False

    if request.is_ajax():
        return False

    return bool(settings.DEBUG)
