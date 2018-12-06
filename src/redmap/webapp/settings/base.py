# -*- coding: utf-8 -*-
# Django settings for webapp project.

import posixpath
import djcelery
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.conf import global_settings
djcelery.setup_loader()

from celery.schedules import crontab
from os import path

from django.utils.functional import lazy, Promise
def lazy_dependant_setting(fn):
    if isinstance(fn, Promise):
        pass
    elif isinstance(fn, basestring):
        fn = fn.format

    def run():
        if not hasattr(run, '_cache'):
            from django.conf import settings
            run._cache = str(fn(settings))
        return run._cache

    return lazy(run, str)()

# Set PROJECT_ROOT to the dir of the current file
SETTINGS_ROOT = path.abspath(path.dirname(__file__))
WEBAPP_ROOT = path.abspath(path.dirname(SETTINGS_ROOT))
PROJ_ROOT = path.abspath(path.dirname(WEBAPP_ROOT))
SRC_ROOT = path.abspath(path.dirname(PROJ_ROOT))
REPO_ROOT = path.abspath(path.dirname(SRC_ROOT))

# VAR_ROOT is the only place this application should be able to write to.
VAR_ROOT = path.join(REPO_ROOT, 'var')

# Paths for assets (static files, uploaded files)
DOCUMENT_ROOT = path.join(VAR_ROOT, 'www')
STATIC_ROOT = path.join(VAR_ROOT, 'static')
MEDIA_ROOT = path.join(VAR_ROOT, 'media')
USE_X_FORWARDED_HOST = True

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

INTERNAL_IPS = [
    "127.0.0.1",
]

SITE_ID = 1

ADMINS = [
    ("OVERRIDE", "OVERRIDE@IN-LOCAL-SETTINGS.PY"),
]

#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
#        "NAME": "dev.db",                       # Or path to database file if using sqlite3.
#        "USER": "",                             # Not used with sqlite3.
#        "PASSWORD": "",                         # Not used with sqlite3.
#        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
#        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
#    }
#}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Australia/Hobart"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-au"

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'redmap.org.au',
    'www.redmap.org.au',
    'staging.redmap.org.au',
]

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = False

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/static/"

FILEMANAGER_UPLOAD_URL = MEDIA_URL + 'uploads/'

# Additional directories which hold static files
STATICFILES_DIRS = [
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    "compressor.finders.CompressorFinder",
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Subdirectory of COMPRESS_ROOT to store the cached media files in
COMPRESS_OUTPUT_DIR = "cache"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'dbtemplates.loader.Loader',
)

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "maintenancemode.middleware.MaintenanceModeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "redmap.webapp.middleware.XUACompatible",
]

ROOT_URLCONF = "redmap.webapp.urls"

# Page templates are found relative to webapp/templates but filtered to cms/page_templates folder
CMS_PAGE_TEMPLATE_PATH = path.join(WEBAPP_ROOT, "page_templates")
CMS_PAGE_TEMPLATE_MATCH = None
CMS_PAGE_TEMPLATE_DEFAULT = "default.html"

TEMPLATE_DIRS = [
    CMS_PAGE_TEMPLATE_PATH,
    path.join(WEBAPP_ROOT, "templates"),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",

    "staticfiles.context_processors.static",
    "zinnia.context_processors.version",
    "redmap.apps.redmapdb.context_processors.nav_regions",
    "redmap.apps.redmapdb.context_processors.sighting_statuses",
    "redmap.webapp.context_processors.testing_flag",
    "redmap.webapp.context_processors.site_base",
    "redmap.apps.cms.context_processors.copy",
    "redmap.apps.frontend.context_processors.content",
    "redmap.apps.frontend.context_processors.resolver_match",
    "redmap.apps.frontend.context_processors.facebook_page_url",
    "redmap.apps.frontend.context_processors.is_section_page",
    "redmap.common.context_processors.redmap_tag",
    "django_facebook.context_processors.facebook",
    "redmap.apps.frontend.context_processors.geoserver_url",
]

AUTHENTICATION_BACKENDS = [
    'django_facebook.auth_backends.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
]

PASSWORD_HASHERS = (
    'redmap.webapp.hashers.RedmapTasSHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    'django.contrib.staticfiles',
    "django.contrib.sitemaps",
    "django.contrib.redirects",
    "micawber.contrib.mcdjango",

    # external
    "haystack",
    "compressor",
    "sorl.thumbnail",
    "emailconfirmation",
    "ajax_validation",
    "timezones",
    "formwizard",
    "singleton_models",
    "ckeditor",
    "filemanager",
    "reversion",
    "registration",
    "django_facebook",
    "privatebeta",
    "djcelery",
    "ajax_forms",
    "gunicorn",
    "django_filters",
    "dbtemplates",
    'rest_framework',
    'rest_framework.authtoken',

    # Zinnia
    "django.contrib.comments",
    "tagging",
    "mptt",
    "zinnia",

    # project
    "redmap.apps.formjs",
    "redmap.apps.redmapdb",
    "redmap.apps.frontend",
    "redmap.apps.backend",
    "redmap.apps.news",
    "redmap.apps.accounts",
    "redmap.apps.cms",
    "redmap.apps.restapi",
    "redmap.apps.surveys",
    "redmap.webapp",
]

AUTH_PROFILE_MODULE = "redmapdb.Person" # used for user profiles

FIXTURE_DIRS = [
    path.join(WEBAPP_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
DEFAULT_FILE_STORAGE = 'redmap.common.util.ASCIIFileSystemStorage'

# Sorl Thumbnail
THUMBNAIL_DEBUG = False
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_UPSCALE = False
THUMBNAIL_DUMMY = False
THUMBNAIL_DUMMY_SOURCE = "http://placehold.it/%(width)sx%(height)s"

# ckeditor
CKEDITOR_MEDIA_PREFIX = path.join(STATIC_URL)
CKEDITOR_UPLOAD_PATH = path.abspath(path.join(MEDIA_ROOT, "uploads"))
FILEMANAGER_UPLOAD_ROOT = CKEDITOR_UPLOAD_PATH

CKEDITOR_BASE_CONFIGS = {
    'width': 610,
    'resize_maxWidth': 600,
    'height': 300,
    'toolbarCanCollapse': False,
    'format_tags': 'p;h2;h3;h4',
    'filebrowserBrowseUrl': reverse_lazy('filemanager'),
    'skin': lazy_dependant_setting('BootstrapCK-Skin,{0.STATIC_URL}reskin/ckeditor/BootstrapCK-Skin/'),
    'contentsCss': lazy_dependant_setting('{0.STATIC_URL}reskin/css/style.css'),
    'bodyId': 'page',
    'bodyClass': 'ckeditor',
}


def merge_ckconfig(extra={}):
    new = {}
    new.update(CKEDITOR_BASE_CONFIGS)
    new.update(extra)
    return new

CKEDITOR_CONFIGS = {
    'basic_toolbar': merge_ckconfig({
        'toolbar': [
            ['Undo', 'Redo'],
            ['PasteText'],
            ['Bold', 'Italic', 'Underline'],
            ['Link', 'Unlink', 'Anchor'],
            ['Format'],
            ['Image'],
            ['SpellChecker', 'Scayt'],
            ['RemoveFormat', 'Source', 'Maximize'],
        ],
        'height': 200,
    }),
    'default': merge_ckconfig({
        'toolbar': [
            ['Undo', 'Redo'],
            ['PasteText'],
            ['Bold', 'Italic', 'Underline'],
            ['Link', 'Unlink', 'Anchor'],
            ['Format', 'RemoveFormat', 'ShowBlocks'],
            ['Image'],
            ['SpellChecker', 'Scayt',],
            ['RemoveFormat', 'Source', 'Maximize'],
        ],
    }),
    'full_toolbar': merge_ckconfig({
        'toolbar': [
            ['Undo', 'Redo'],
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ['Bold', 'Italic', 'Underline'],
            ['Link', 'Unlink', 'Anchor'],
            ['Format', 'RemoveFormat', 'ShowBlocks'],
            ['Image', 'Table', 'SpecialChar', 'HorizontalRule'],
            ['SpellChecker', 'Scayt'],
            ['BulletedList', 'NumberedList'],
            ['RemoveFormat', 'Source', 'Maximize'],
        ],
    }),
    'inline_styles': merge_ckconfig({
        'toolbar': [
            ['Bold', 'Italic', 'Underline'],
        ],
        'toolbarCanCollapse': True,
    }),
}

# Application settings
REDMAP_SPECIES_GROUP = 1

VALID_SIGHTING = 'VLD'
INVALID_SIGHTING = 'IVD'
REQUIRES_VALIDATION = 'UKN'
REASSIGNED = 'REA'
SPAM_SIGHTING = 'SPM'

GEOSERVER_URL = 'http://geoserver.imas.utas.edu.au/geoserver/redmap/wms'

# These are hardcoded but exists in database
PHOTO_RADIOGROUP_SECTION = "photo_radiogroup"
PHOTO_CHECKBOXES_SECTION = "photo_checkboxes"
LOCATION_CHECKBOXES_SECTION = "location_checkboxes"
CHARACTERISTICS_CHECKBOXES_SECTION = "characteristics_checkboxes"
PHOTO_MATCHES_SPECIES_QUESTION = "Photo identifies the species"
PHOTO_MATCHES_SPECIES_ANSWERS = ("Yes", "No", "Maybe")

REDMAP_TAG = "redmap"  # we will perform an iregex on tag names to find this tag

# django-registration settings
ACCOUNT_ACTIVATION_DAYS = 7
# EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'noreply@redmap.org.au'
LOGIN_REDIRECT_URL = '/'

# django_facebook settings
FACEBOOK_APP_ID = 'OVERRIDE_IN_LOCAL_SETTINGS.PY'
FACEBOOK_APP_SECRET = 'OVERRIDE_IN_LOCAL_SETTINGS.PY'
FACEBOOK_LOGIN_DEFAULT_REDIRECT = '/'
FACEBOOK_REGISTRATION_REDIRECT = '/my-redmap/?facebook_welcome=true'
FACEBOOK_REGISTRATION_TEMPLATE = 'registration/registration_form.html'
FACEBOOK_DEFAULT_SCOPE = ['email', 'user_about_me', 'user_birthday', 'user_website', 'publish_actions']

FACBOOK_REDMAP_NAMESPACE = 'OVERRIDE_IN_LOCAL_SETTINGS.PY'
FACBOOK_REDMAP_SIGHTING_ACTION = 'log'
FACBOOK_REDMAP_SIGHTING_OBJECT = 'valid_sighting'

# other facebook settings
FACEBOOK_PAGE_URL = 'http://www.facebook.com/RedmapAustralia'

# celery
CELERYBEAT_SCHEDULE = {
    "check-stale-sightings-daily": {
        "task": "process_stale_sightings",
        "schedule": crontab(hour=9),
    },
}
BROKER_URL = 'redis://127.0.0.1:6379/0'

REDMAP_MODELS_USE_MSSQL = True

MESSAGE_TAGS = {
    messages.DEBUG: 'alert alert-info',
    messages.INFO: 'alert alert-info',
    messages.SUCCESS: 'alert alert-success',
    messages.WARNING: 'alert alert-block',
    messages.ERROR: 'alert alert-error',
}


HAYSTACK_SITECONF = 'redmap.webapp.search_sites'
HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_XAPIAN_PATH = path.join(VAR_ROOT, 'xapian_index')

ENQUIRIES_EMAIL = 'enquiries@redmap.org.au'

MAINTENANCE_MODE = False

DBTEMPLATES_USE_REVERSION = True
# DBTEMPLATES_ADD_DEFAULT_SITE=True
DBTEMPLATES_USE_CODEMIRROR = True

REST_FRAMEWORK = {
    'FILTER_BACKEND': 'rest_framework.filters.DjangoFilterBackend',
    'PAGINATE_BY': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# GeoServer settings
WMS_BASE_URL = "http://geoserver.imas.utas.edu.au/geoserver/redmap/wms"

# Sane defaults for fetching
WMS_DISTRIBUTION_PARAMS = dict(
    service="WMS",
    version="1.1.0",
    request="GetMap",
    styles="",
    bbox="1.237199884670033E7,-5516608.554242996,1.7218876832381703E7,-892319.0468662267",
    srs="EPSG:900913",
    format="image/png",
    layers="redmap:MB_SPECIES_DISTRIBUTION_REDMAP_VIEW",
    width="200",
    height="200",
    transparent="TRUE",
    # CQL_FILTER="(ID=XXX)",
)

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

MANAGERS = ADMINS

ZINNIA_ENTRY_BASE_MODEL = 'redmap.apps.news.entry.Entry'
ZINNIA_PING_EXTERNAL_URLS = False
ZINNIA_SAVE_PING_DIRECTORIES = False
ZINNIA_ENTRY_TEMPLATES = [
    ('zinnia/single_article_1.html', 'Single Article 1'),
    ('zinnia/single_article_2_photos_left.html', 'Single Article 2 (Photos left)'),
    ('zinnia/single_article_3_photos_below.html', 'Single Article 3 (Photos below)'),
    ('zinnia/single_article_4_wide_photos_below.html', 'Single Article 4 (Wide photos below)'),
]

MAINTENANCE_IGNORE_URLS = (
    r'^/admin/.*',
    r'^/static/.*',
)

# TEST_RUNNER = 'redmap.tests.RedmapDiscoverRunner'
TEST_RUNNER = 'discover_runner.runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = path.join(PROJ_ROOT)

SERIALIZATION_MODULES = {
    'json2': 'wadofstuff.django.serializers.json'
}

import sys
TESTING = sys.argv[1:2] == ['test']  # TODO: there must be a cleaner way
