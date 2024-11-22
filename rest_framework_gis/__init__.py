VERSION = (1, 1, 0, 'final')
__version__ = VERSION  # alias


def get_version():
    version = f'{VERSION[0]}.{VERSION[1]}'
    if VERSION[2]:
        version = f'{version}.{VERSION[2]}'
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = f'{version} {VERSION[3]}'
    return version
