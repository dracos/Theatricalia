# Django settings for theatricalia project.

# My additions
import os.path, sys
OUR_ROOT = os.path.realpath(os.path.dirname(__file__))
ext = os.path.join(OUR_ROOT, 'ext')
if ext not in sys.path:
    sys.path.insert(0, ext)

ALPHA_PASSWORD='tiaomiwym' # this, if anything of mine, is worth your memory

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'Matthew Somerville <matthew@theatricalia.com>'
SERVER_EMAIL = 'matthew@theatricalia.com'

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

LOGIN_URL = '/tickets'
LOGIN_REDIRECT_URL = '/profile'
AUTHENTICATION_BACKENDS = (
    'profiles.backends.ModelBackend',
)
AUTH_PROFILE_MODULE = 'profiles.profile'

APPEND_SLASH = False

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Matthew Somerville', 'matthew@theatricalia.com'),
)

INTERNAL_IPS = ('127.0.0.1',)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'theatricalia' # Or path to database file if using sqlite3.
DATABASE_USER = 'theatricalia' # Not used with sqlite3.
DATABASE_PASSWORD = 'Lq6BSrC6RFRepEC2'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(OUR_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'z)iry(aa$xl^k-v&s(c1@*%9p+9m38c)^3orpb3b58njw9y9lq'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'theatricalia.middleware.AlphaMiddleware',
    'theatricalia.middleware.OnlyLowercaseUrls',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'theatricalia.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(OUR_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes', # Attaching things to multiple models - comments, photos
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.humanize', # Ordinals
    'django.contrib.webdesign', # Lorem
    #'django.contrib.sites',
    'django.contrib.admin',
    'sorl.thumbnail',
    'reversion',
    'countries',
    'theatricalia.common',
    'theatricalia.places',
    'theatricalia.plays',
    'theatricalia.productions',
    'theatricalia.photos',
    'theatricalia.people',
    'theatricalia.profiles',
    'theatricalia.news',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    #'django.core.context_processors.i18n',
    #'django.core.context_processors.media',
)

