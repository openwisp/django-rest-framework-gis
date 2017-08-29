from math import cos, pi

from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis import forms
from django.utils import six

from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ParseError

from .tilenames import tile_edges

try:
    import django_filters
except ImportError:  # pragma: no cover
    raise ImproperlyConfigured(
        'restframework-gis filters depend on package "django-filter" '
        'which is missing. Install with "pip install django-filter".'
    )

try:  # pragma: no cover
    # django >= 1.8
    from django.contrib.gis.db.models.lookups import gis_lookups
except ImportError:  # pragma: no cover
    # django <= 1.7
    gis_lookups = models.sql.query.ALL_TERMS


__all__ = [
    'InBBoxFilter',
    'InBBOXFilter',
    'GeometryFilter',
    'GeoFilterSet',
    'TMSTileFilter',
    'DistanceToPointFilter'
]


class InBBoxFilter(BaseFilterBackend):
    bbox_param = 'in_bbox'  # The URL query parameter which contains the bbox.
    tile_param = None  # Compatibility for tile class

    def get_filter_bbox(self, request, query_param=None):
        bbox_string = request.query_params.get(query_param, None)
        if not bbox_string:
            return None

        try:
            p1x, p1y, p2x, p2y = (float(n) for n in bbox_string.split(','))
        except ValueError:
            raise ParseError('Invalid bbox string supplied for parameter {0}'.format(query_param))

        x = Polygon.from_bbox((p1x, p1y, p2x, p2y))
        return x

    def filter_queryset(self, request, queryset, view):
        query_filter = {}
        self.bbox_params = getattr(
            view,
            'bbox_params', {
                self.tile_param or self.bbox_param: {
                    'filter_field': getattr(view,'bbox_filter_field', None),
                    'include_overlapping': getattr(view,'bbox_filter_include_overlapping', False)
                }
            }
        )
        for query_param, filter_field_attributes in six.iteritems(self.bbox_params):
            filter_field = filter_field_attributes['filter_field']
            if not filter_field:
                continue

            bbox = self.get_filter_bbox(request, query_param)
            if not bbox:
                continue

            include_overlapping = filter_field_attributes['include_overlapping']
            if include_overlapping:
                geoDjango_filter = 'bboverlaps'
            else:
                geoDjango_filter = 'contained'

            # build the dict then return queryset filter that filters multiple attributes
            # backwards compatibile because get_filter_bbox is private and untested method
            query_filter['%s__%s' % (filter_field, geoDjango_filter)]= bbox
        if query_filter == {}:
            return queryset
        return queryset.filter(Q(**query_filter))


# backward compatibility
InBBOXFilter = InBBoxFilter


class GeometryFilter(django_filters.Filter):
    field_class = forms.GeometryField

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', forms.BaseGeometryWidget)
        super(GeometryFilter, self).__init__(*args, **kwargs)


class GeoFilterSet(django_filters.FilterSet):
    GEOFILTER_FOR_DBFIELD_DEFAULTS = {
        models.GeometryField: {
            'filter_class': GeometryFilter
        },
    }

    def __new__(cls, *args, **kwargs):
        try:
            cls._meta.filter_overrides.update(cls.GEOFILTER_FOR_DBFIELD_DEFAULTS)
        # maintain compatibility for django-filter < 0.15
        except AttributeError:  # pragma: nocover
            cls.filter_overrides.update(cls.GEOFILTER_FOR_DBFIELD_DEFAULTS)
        cls.LOOKUP_TYPES = sorted(gis_lookups)
        return super(GeoFilterSet, cls).__new__(cls)


class TMSTileFilter(InBBoxFilter):
    tile_param = 'tile'  # The URL query paramater which contains the tile address

    def get_filter_bbox(self, request, query_param=None):
        tile_string = request.query_params.get(query_param, None)
        if not tile_string:
            return None

        try:
            z, x, y = (int(n) for n in tile_string.split('/'))
        except ValueError:
            raise ParseError('Invalid tile string supplied for parameter {0}'.format(query_param))

        bbox = Polygon.from_bbox(tile_edges(x, y, z))
        return bbox


class DistanceToPointFilter(BaseFilterBackend):
    dist_param = 'dist'
    point_param = 'point'  # The URL query parameter which contains the

    def get_filter_point(self, request):
        point_string = request.query_params.get(self.point_param, None)
        if not point_string:
            return None

        try:
            (x, y) = (float(n) for n in point_string.split(','))
        except ValueError:
            raise ParseError('Invalid geometry string supplied for parameter {0}'.format(self.point_param))

        p = Point(x, y)
        return p

    def dist_to_deg(self, distance, latitude):
        """
        distance = distance in meters
        latitude = latitude in degrees

        at the equator, the distance of one degree is equal in latitude and longitude.
        at higher latitudes, a degree longitude is shorter in length, proportional to cos(latitude)
        http://en.wikipedia.org/wiki/Decimal_degrees

        This function is part of a distance filter where the database 'distance' is in degrees.
        There's no good single-valued answer to this problem.
        The distance/ degree is quite constant N/S around the earth (latitude),
        but varies over a huge range E/W (longitude).

        Split the difference: I'm going to average the the degrees latitude and degrees longitude
        corresponding to the given distance. At high latitudes, this will be too short N/S
        and too long E/W. It splits the errors between the two axes.

        Errors are < 25 percent for latitudes < 60 degrees N/S.
        """
        #   d * (180 / pi) / earthRadius   ==> degrees longitude
        #   (degrees longitude) / cos(latitude)  ==> degrees latitude
        lat = latitude if latitude >= 0 else -1 * latitude
        rad2deg = 180 / pi
        earthRadius = 6378160.0
        latitudeCorrection = 0.5 * (1 + cos(lat * pi / 180))
        return (distance / (earthRadius * latitudeCorrection) * rad2deg)

    def filter_queryset(self, request, queryset, view):
        filter_field = getattr(view, 'distance_filter_field', None)
        convert_distance_input = getattr(view, 'distance_filter_convert_meters', False)
        geoDjango_filter = 'dwithin'  # use dwithin for points

        if not filter_field:
            return queryset

        point = self.get_filter_point(request)
        if not point:
            return queryset

        # distance in meters
        dist_string = request.query_params.get(self.dist_param, 1000)
        try:
            dist = float(dist_string)
        except ValueError:
            raise ParseError('Invalid distance string supplied for parameter {0}'.format(self.dist_param))

        if (convert_distance_input):
            # Warning:  assumes that the point is (lon,lat)
            dist = self.dist_to_deg(dist, point[1])

        return queryset.filter(Q(**{'%s__%s' % (filter_field, geoDjango_filter): (point, dist)}))
