import os

TEST_PERFORMANCE = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_restframework_gis',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '',  # Change to 'postgres' for docker-compose.yml testing to work
        'PORT': '',
    },
}

SECRET_KEY = 'fn)t*+$)ugeyip6-#txyy$5wf2ervc0d2n#h)qb)y5@ly$t*@w'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # rest framework
    'rest_framework',
    'rest_framework_gis',
    # test app
    'django_restframework_gis_tests',
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

ROOT_URLCONF = 'urls'

TIME_ZONE = 'Europe/Rome'
LANGUAGE_CODE = 'en-gb'
USE_TZ = True
USE_I18N = False
USE_L10N = False
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = '%s/media/' % SITE_ROOT
MEDIA_URL = '/media/'
STATIC_ROOT = '%s/static/' % SITE_ROOT
STATIC_URL = '/static/'

TEMPLATE_STRING_IF_INVALID = 'INVALID_TEMPLATE: %s END_INVALID_TEMPLATE'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework_gis.schema.GeoFeatureAutoSchema',
}

# local settings must be imported before test runner otherwise they'll be ignored
try:
    from local_settings import *
except ImportError:
    pass
