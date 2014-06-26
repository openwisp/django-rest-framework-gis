from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon
from django.contrib.gis import forms

from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ParseError

try:
    import django_filters
except ImportError:
    raise ImproperlyConfigured(
        'restframework-gis filters depend on package "django-filter" '
        'which is missing. Install with "pip install django-filter".'
    )


__all__ = [
    'InBBOXFilter',
    'GeometryFilter',
    'GeoFilterSet'
]


class InBBOXFilter(BaseFilterBackend):

    bbox_param = 'in_bbox'  # The URL query parameter which contains the bbox.

    def get_filter_bbox(self, request):
        bbox_string = request.QUERY_PARAMS.get(self.bbox_param, None)
        if not bbox_string:
            return None

        try:
            p1x, p1y, p2x, p2y = (float(n) for n in bbox_string.split(','))
        except ValueError:
            raise ParseError("Not valid bbox string in parameter %s."
                             % self.bbox_param)

        x = Polygon.from_bbox((p1x, p1y, p2x, p2y))
        return x

    def filter_queryset(self, request, queryset, view):
        filter_field = getattr(view, 'bbox_filter_field', None)
        include_overlapping = getattr(view, 'bbox_filter_include_overlapping', False)
        if include_overlapping:
            geoDjango_filter = 'bboverlaps'
        else:
            geoDjango_filter = 'contained'

        if not filter_field:
            return queryset

        bbox = self.get_filter_bbox(request)
        if not bbox:
            return queryset
        return queryset.filter(Q(**{'%s__%s' % (filter_field, geoDjango_filter): bbox}))


class GeometryFilter(django_filters.Filter):
    field_class = forms.GeometryField


class GeoFilterSet(django_filters.FilterSet):
    GEOFILTER_FOR_DBFIELD_DEFAULTS = {
        models.GeometryField: {
            'filter_class': GeometryFilter
        },
    }

    def __new__(cls, *args, **kwargs):
        cls.filter_overrides.update(cls.GEOFILTER_FOR_DBFIELD_DEFAULTS)
        cls.LOOKUP_TYPES = sorted(models.sql.query.ALL_TERMS)
        return super(GeoFilterSet, cls).__new__(cls)