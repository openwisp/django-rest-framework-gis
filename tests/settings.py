import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_restframework_gis',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '',
        'PORT': ''
    },
}

SECRET_KEY = 'fn)t*+$)ugeyip6-#txyy$5wf2ervc0d2n#h)qb)y5@ly$t*@w'

INSTALLED_APPS = (
    # rest framework
    'rest_framework',
    'rest_framework_gis',
    
    # test app
    'django_restframework_gis_tests'
)

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

# local settings must be imported before test runner otherwise they'll be ignored
try:
    from local_settings import *
except ImportError:
    pass
