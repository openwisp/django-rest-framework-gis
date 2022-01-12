import django

VERSION = (0, 18, 0, 'final')
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


if django.VERSION < (3, 2):
    default_app_config = 'rest_framework_gis.apps.AppConfig'
