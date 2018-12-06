"""
Settings for the development environment
"""
from redmap.webapp.settings.base import *

DEBUG = True
COMPRESS = not DEBUG

REDMAP_MODELS_USE_MSSQL = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': path.join(VAR_ROOT, 'db.sqlite'),                       # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    },
}

INSTALLED_APPS += [
    'django_extensions',
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_CONFIRMATION_DAYS = 31

THUMBNAIL_DUMMY = False
THUMBNAIL_DUMMY_SOURCE = "http://placehold.it/%(width)sx%(height)s"

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
            },
        }
}

try:
    from redmap.webapp.settings.local_settings import *
except ImportError:
    pass
