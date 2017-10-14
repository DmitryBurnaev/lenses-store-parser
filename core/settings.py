# -*- coding: utf-8 -*-
import os
import sys

from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '3i0vre48*dnk7oh9thju$z%i0ktys&n@90vox4xdcwrtta3dn&'

sys.path.append(os.path.join(BASE_DIR, "core"))
sys.path.append(os.path.join(BASE_DIR, "modules"))

DEBUG = False

ALLOWED_HOSTS = []

MODULES = [
    'main',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
] + MODULES

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'common.context_processors.base_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
    }
}

# Internationalization

TIME_ZONE = 'Europe/Moscow'

LANGUAGE_CODE = 'ru'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] "
                      "%(message)s",
            'datefmt': "%d%b %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'formatter': 'standard',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {},
}

# add logic of logging to modules
for app in MODULES:
    LOGGING['loggers'][app] = {
        'handlers': ['mail_admins'],
        'level': 'DEBUG',
        'propagate': True,
    }

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_SERIALIZER = 'pickle'

CELERY_RESULT_BACKEND = 'redis://'
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
CELERY_RESULT_SERIALIZER = 'pickle'

CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1

from kombu import Queue

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_QUEUES = (
    Queue('default', routing_key='default'),            # все задачи
)
CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_SEND_TASK_ERROR_EMAILS = True

DEBUG_INTERNAL_IPS = []

# дельта по времени через сколько можно запскать новый парсинг (в секундах)
ALLOWED_PARSE_TIMEDELTA = 30 * 60


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

ARCHIVE_WEEKS_COUNT = 5
MANAGERS = []
DEFAULT_FROM_EMAIL = 'test@example.com'

CELERYBEAT_SCHEDULE = {}

PARSE_RESULT_PAGINATE_BY = 10

from settings_local import *

if not LOCAL_DATABASES:
    raise ImproperlyConfigured("LOCAL_DATABASES don't configure")

DATABASES.update(LOCAL_DATABASES)

if DEBUG:
    INTERNAL_IPS = DEBUG_INTERNAL_IPS
    DISABLE_PANELS = []
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda x: True
    }

    # additional modules for development
    INSTALLED_APPS += (
        'debug_toolbar',
    )
