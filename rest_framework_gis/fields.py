import six  # TODO Remove this along with GeoJsonDict when support for python 2.6/2.7 is dropped.
import json
from collections import OrderedDict

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import GDALException
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import Field, SerializerMethodField


__all__ = ['GeometryField', 'GeometrySerializerMethodField']


def recursive_round(v, precision):
    """
    Round all numbers within an array or nested arrays
      v: number or nested array of numbers
      precision: integer value of number of decimals to keep
    """
    if hasattr(v, '__iter__'):
        return tuple(recursive_round(x, precision) for x in v)
    return round(v, precision)


def _rm_dupes(coordinates, close=True):
    """
    Return array with no repeating coordinates.
      coordinates: array of coordinates
      close: whether there should always be at least two sets of coordinates, 
        in which case the first set will be repeated twice
    """
    output = []
    for coord in coordinates:
        if not output or coord != output[-1]:
            output.append(coord)
    if close and len(output) == 1:
        output.append(output[0])
    return output

# assert _rm_dupes([(1,1), (1,1), (1,1), (1,1)], False) == [(1, 1)]
# assert _rm_dupes([(1,1), (1,1), (1,1), (1,1)], True) == [(1, 1), (1, 1)]
# assert _rm_dupes([(1,0), (1,1), (1,1), (0,1)], True) == _rm_dupes([(1,0), (1,1), (1,1), (0,1)], False) == [(1, 0), (1, 1), (0, 1)]


def rm_redundant_points(coordinates, geotype):
    if geotype in ('MultiPoint', 'LineString'):
        return _rm_dupes(coordinates, close=(geotype == 'LineString'))
    if geotype in ('MultiLineString', 'Polygon'):
        return _rm_dupes(
            [rm_redundant_points(c, 'LineString') for c in coordinates],
            close=False
        )
    if geotype == 'MultiPolygon':
        return _rm_dupes(
            [rm_redundant_points(c, 'Polygon') for c in coordinates],
            close=True)
    return coordinates


class GeometryField(Field):
    """
    A field to handle GeoDjango Geometry fields
    """
    type_name = 'GeometryField'

    def __init__(self, precision=None, remove_duplicates=False, **kwargs):
        self.precision = precision
        self.rm_dupes = remove_duplicates
        super(GeometryField, self).__init__(**kwargs)
        self.style = {'base_template': 'textarea.html'}

    def to_representation(self, value):
        if isinstance(value, dict) or value is None:
            return value
        # we expect value to be a GEOSGeometry instance
        geojson = GeoJsonDict(value.geojson)
        if self.precision is not None:
            coords = recursive_round(geojson['coordinates'], self.precision)
            geojson['coordinates'] = coords
        if self.rm_dupes:
            geojson['coordinates'] = rm_redundant_points(
                geojson['coordinates'], geojson['type'])
        return geojson

    def to_internal_value(self, value):
        if value == '' or value is None:
            return value
        if isinstance(value, GEOSGeometry):
            # value already has the correct representation
            return value
        if isinstance(value, dict):
            value = json.dumps(value)
        try:
            return GEOSGeometry(value)
        except (GEOSException):
            raise ValidationError(_('Invalid format: string or unicode input unrecognized as GeoJSON, WKT EWKT or HEXEWKB.'))
        except (ValueError, TypeError, GDALException) as e:
            raise ValidationError(_('Unable to convert to python object: {}'.format(str(e))))

    def validate_empty_values(self, data):
        if data == '':
            self.fail('required')
        return super(GeometryField, self).validate_empty_values(data)


class GeometrySerializerMethodField(SerializerMethodField):
    def to_representation(self, value):
        value = super(GeometrySerializerMethodField, self).to_representation(value)
        if value is not None:
            # we expect value to be a GEOSGeometry instance
            return GeoJsonDict(value.geojson)
        else:
            return None


class GeoJsonDict(OrderedDict):
    """
    Used for serializing GIS values to GeoJSON values
    TODO: remove this when support for python 2.6/2.7 will be dropped
    """
    def __init__(self, *args, **kwargs):
        """
        If a string is passed attempt to pass it through json.loads,
        because it should be a geojson formatted string.
        """
        if args and isinstance(args[0], six.string_types):
            try:
                geojson = json.loads(args[0])
                args = (geojson,)
            except ValueError:
                pass
        super(GeoJsonDict, self).__init__(*args, **kwargs)

    def __str__(self):
        """
        Avoid displaying strings like
        ``{ 'type': u'Point', 'coordinates': [12, 32] }``
        in DRF browsable UI inputs (python 2.6/2.7)
        see: https://github.com/djangonauts/django-rest-framework-gis/pull/60
        """
        return json.dumps(self)
