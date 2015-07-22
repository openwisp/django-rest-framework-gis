VERSION = (0, 9, 3, 'final')
__version__ = VERSION  # alias


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s' % (version, VERSION[3])
    return version


default_app_config = 'rest_framework_gis.apps.AppConfig'

# retain support for django 1.5 and 1.6
try:
    import django
    import os

    if os.environ.get('DJANGO_SETTINGS_MODULE') and django.get_version() < '1.7':
        from .apps import AppConfig
        AppConfig().ready()
except ImportError:
    pass
