# Django settings for ak project.
import os
#import sys
PROJECT_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# Django settings for squash project.


FORCE_SCRIPT_NAME = '/irkutsk'
DEBUG = True 
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'squash_irkutsk',                      	# Or path to database file if using sqlite3.
        'USER': 'squash',                      	# Not used with sqlite3.
        'PASSWORD': 'squash014454',                  	# Not used with sqlite3.
        'HOST': 'localhost',                      	# Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      	# Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Irkutsk'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

LANGUAGE_CODE = 'ru'

gettext = lambda s: s
LANGUAGES = [
    ('ru', gettext('Russian')),
    ('en', gettext('English')),
]

SITE_ID = 1


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #STATIC_ROOT,
    #os.path.join(PROJECT_PATH, "admin_tools"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v2_tnrvcw669t&y20q6uo_ka_p1s(ekw-d!6!h+ujd%!zr5xc*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.cache.CacheMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'middlewares.middleware.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "templates")
)

MODELTRANSLATION_TRANSLATION_REGISTRY = 'translation'

INSTALLED_APPS = (
    #'admin_tools',
    #'admin_tools.theming',
    #'admin_tools.menu',
    #'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.flatpages',
    
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'livesettings',
    'tinymce',
    
    'modeltranslation',
    
    'rating',
    'league',

    'google_analytics',
    'rosetta',
    'emailconfirmation',
    'uni_form',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.twitter',
    'allauth.openid',
    'allauth.facebook',
    
    'admin_jqueryui',
    
    'south',
    
    'django_extensions',
    
)

GOOGLE_ANALYTICS_MODEL = True
TEMPLATE_CONTEXT_PROCESSORS = (
    # default template context processors
    'django.contrib.auth.context_processors.auth',
    #'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',

    # django 1.2 only
    #'django.contrib.messages.context_processors.messages', 

    # required by django-admin-tools
    'django.core.context_processors.request',
    
    "allauth.context_processors.allauth",
    "allauth.account.context_processors.account",
    
    "rating.context_processors.site",
    "rating.context_processors.current_rating_datetime",
)
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

RATING_MAX_COMPETITORS_COUNT = 32
RATING_LAST_TOURNAMENTS_COUNT = 8
RATING_RESULT_TOURNAMENTS_COUNT = 4
CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24 * 30
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'rating_cache',
        'TIMEOUT': 60 * 60 * 24 * 30,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCE': 2,
        }
    },
    'league': {
        #'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'BACKEND': 'league.cache.LeagueCache',
        'LOCATION': 'league_cache',
        'TIMEOUT': 60 * 60 * 24 * 30 * 6,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCE': 2,
        }
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PROJECT_PATH, "media/app-messages")
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = '25'
EMAIL_HOST_USER = 'robot@kortov.net'
EMAIL_HOST_PASSWORD = '014454'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'robot@kortov.net'

LOGIN_REDIRECT_URL = '/'

EMAIL_CONFIRMATION_DAYS = 1

ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
