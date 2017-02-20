"""
Django settings for hoffpw project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3-jl153nj14q_*&gw^lkg8jrq1#30jtsjbm0lmt=xptok1!(ee'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['api.hoff.pw']

# SSL ( It seems not now, can't have heroku ssl on custom domain for free.
"""
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
"""

# Celery settings
#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_BROKER_URL = os.environ.get('CLOUDAMQP_URL')
CELERY_BROKER_POOL_LIMIT = 1 # Will decrease connection usage
CELERY_BROKER_HEARTBEAT = None # We're using TCP keep-alive instead
CELERY_BROKER_CONNECTION_TIMEOUT = 30 # May require a long timeout due to Linux DNS timeouts etc
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = None # AMQP is not recommended as result backend as it creates thousands of queues
CELERY_SEND_EVENTS = False # Will not create celeryev.* queues
CELERY_EVENT_QUEUE_EXPIRES = 60 # Will delete all celeryev. queues without consumers after 1 minute.
CELERY_TASK_SERIALIZER = 'json'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'webauth',
    'twitch_stats',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hoffpw.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hoffpw.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAdminUser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'webauth.authentication.CustomTokenAuthentication',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'PAGE_SIZE': 10
}


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# CORS

CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'webauth.User'

AUTHENTICATION_BACKENDS = [
    'webauth.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Update database configuration with $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

try:
    from .local_settings import *
except ImportError:
    pass
