try:
    from collections import OrderedDict  # noqa
# python 2.6
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict  # noqa
