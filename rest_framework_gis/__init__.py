VERSION = (0, 9, 5, 'final')
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

# maintain support for django 1.5 and 1.6
# TODO: remove in version 1.0
try:
    import os
    import django

    if os.environ.get('DJANGO_SETTINGS_MODULE'):
        from django.conf import settings
        from .apps import AppConfig

        if 'rest_framework_gis' not in settings.INSTALLED_APPS:
            import warnings
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn('\nGeoModelSerializer is deprecated, '
                          'add "rest_framework_gis" to settings.INSTALLED_APPS and use '
                          '"rest_framework.ModelSerializer" instead',
                          DeprecationWarning)

        if django.get_version() < '1.7' or 'rest_framework_gis' not in settings.INSTALLED_APPS:
            import rest_framework_gis
            AppConfig('rest_framework_gis', rest_framework_gis).ready()
except ImportError:
    pass
