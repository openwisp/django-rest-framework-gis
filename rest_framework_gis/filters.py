from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon
from django.contrib.gis import forms

from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ParseError

from .tilenames import tile_edges

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
    'GeoFilterSet',
    'TMSTileFilter',
    'DistanceFilter'
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


class TMSTileFilter(InBBOXFilter):

    tile_param = 'tile' # The URL query paramater which contains the tile address

    def get_filter_bbox(self, request):
        tile_string = request.QUERY_PARAMS.get(self.tile_param, None)
        if not tile_string:
            return None

        try:
            z, x, y = (int(n) for n in tile_string.split('/'))
        except ValueError:
            raise ParseError("Not valid tile string in parameter %s."
                             % self.tile_param)

        bbox = Polygon.from_bbox(tile_edges(x, y, z))
        return bbox


class DistanceFilter(BaseFilterBackend):

    geom_param = 'geom'  # The URL query parameter which contains the bbox.

    def get_filter_geom(self, request):
        geom_string = request.QUERY_PARAMS.get(self.geom_param, None)
        if not geom_string:
            return None

        try:
            points = (float(n) for n in geom_string.split(','))
        except ValueError:
            raise ParseError("Not valid geometry string in parameter %s."
                             % self.geom_param)

        x = Polygon.from_geom(points)
        return x

    
    def distToDeg(distance, latitude):
        """
        distance = distance in meters
        latitude = latitude in degrees 
        As one moves away from the equator towards a pole, one degree of longitude is 
        multiplied by the cosine of the latitude, decreasing the distance. 
        http://en.wikipedia.org/wiki/Decimal_degrees

        There's no good solution here, the distance/ degree is quite constant N/S around the earth,
        but varies over a huge range E/W. 
        Split the difference: I'm going to average the the degrees latitude and degrees longitude 
        corresponding to the given distance. This will be too short N/S and too long E/W, 
        but less so than no correction. 

        Errors are < 25% for latitude < 70° N/S.
        """
        #   d * (180 / pi) / earthRadius   ==> degrees longitude
        #   (degrees longitude) / cos(latitude)  ==> degrees latitude
        latitude if latitude >= 0 else -1*latitude 
        rad2deg = 180/math.pi
        earthRadius = 6378160.0
        latitudeCorrection = 0.5 * (1 + cos(latitude * math.pi / 180))
        return (distance / (earthRadius * latitudeCorrection) * rad2deg)


    def filter_queryset(self, request, queryset, view):
        filter_field = getattr(view, 'distance_filter_field', None)

        geoDjango_filter = 'dwithin'  # use dwithin or geom.buffer with overlaps/contains?

        if not filter_field:
            return queryset

        geom = self.get_filter_geom(request)
        if not geom:
            return queryset

        # distance in meters
        dist_string = request.QUERY_PARAMS.get(self.dist_param, 100)
        try:
            dist = float(dist_string)
        except ValueError:
            raise ParseError("Not valid distance string in parameter %s."
                             % self.dist_param)

        if (geom.srid == 4326): # or other projections in degrees
            dist = distToDeg(dist, geom.centroid[1])
            
        return queryset.filter(Q(**{'%s__%s' % (filter_field, geoDjango_filter): (geom, dist)}))
