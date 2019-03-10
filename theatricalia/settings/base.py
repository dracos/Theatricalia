# Django settings for theatricalia project.

import os
SETTINGS_DIR = os.path.realpath(os.path.dirname(__file__))
OUR_ROOT = os.path.join(SETTINGS_DIR, '..', '..')

EMAIL_LOCALPART = 'principal'
EMAIL_DOMAIN = 'theatricalia.com'
EMAIL_FULL = '%s@%s' % (EMAIL_LOCALPART, EMAIL_DOMAIN)

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'Matthew Somerville <%s>' % EMAIL_FULL
SERVER_EMAIL = EMAIL_FULL

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_SECONDS = 300

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_URL = '/tickets'
LOGIN_REDIRECT_URL = '/profile'
AUTHENTICATION_BACKENDS = (
    'profiles.backends.ModelBackend',
)
AUTH_USER_MODEL = 'profiles.User'

APPEND_SLASH = False

if 'staging' in OUR_ROOT:
    DEBUG = True
else:
    DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

ADMINS = (
    ('Matthew Somerville', EMAIL_FULL),
)

INTERNAL_IPS = ('127.0.0.1',)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'theatricalia',
        'USER': 'theatricalia',
        'CONN_MAX_AGE': None,
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SOUTH_TESTS_MIGRATE = False
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

ALLOWED_HOSTS = [ 'theatricalia.com', 'theatricalia.com.', 'localhost', 'staging.theatricalia.com' ]

# Local time zone for this installation. Choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

USE_L10N = True
USE_TZ = False

MEDIA_ROOT = os.path.join(OUR_ROOT, '..', 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(OUR_ROOT, '..', 'collected_static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(OUR_ROOT, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'theatricalia.middleware.RemoteAddrMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #'theatricalia.middleware.AlphaMiddleware',
    'theatricalia.middleware.OnlyLowercaseUrls',
    'theatricalia.middleware.RemoveSlashMiddleware',
    'reversion.middleware.RevisionMiddleware',
]
if DEBUG:
    MIDDLEWARE_CLASSES.insert(5, 'debug_toolbar.middleware.DebugToolbarMiddleware')

if 'staging' not in OUR_ROOT:
    SECURE_HSTS_SECONDS = 31536000
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

ROOT_URLCONF = 'theatricalia.urls'
WSGI_APPLICATION = 'theatricalia.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(OUR_ROOT, 'templates'),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes', # Attaching things to multiple models - comments, photos
    'django_comments',
    'django.contrib.sessions',
    'django.contrib.humanize', # Ordinals
    'django.contrib.webdesign', # Lorem
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'sorl.thumbnail',
    'reversion',
    'countries',
    'django_nose',
    'common',
    'places',
    'plays',
    'productions',
    'photos',
    'people',
    'profiles',
    'news',
    'merged',
    'lp',
]
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.contrib.messages.context_processors.messages',
    #'django.core.context_processors.i18n',
    'django.core.context_processors.media',
)

from django.db.utils import OperationalError
def skip_too_many_connections(record):
    if record.exc_info:
        exc_type, exc_value = record.exc_info[:2]
        if exc_type == OperationalError and exc_value.args[0] == 1040:
            return False
    return True

def skip_new_content_types(record):
    if record.exc_info:
        exc_type, exc_value = record.exc_info[:2]
        if exc_type == RuntimeError and 'Error creating new content types' in exc_value.args[0]:
            return False
    return True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'not_too_many_connections': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_too_many_connections, 
        },
        'not_new_content_types': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_new_content_types,
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'not_new_content_types', 'not_too_many_connections'],
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

# Monkeypatches

# To have aria-required on required form fields
from django.forms import fields
def aria_widget_attrs(self, widget):
    if self.required:
        return { 'aria-required': 'true' }
    return {}
fields.Field.widget_attrs = aria_widget_attrs

