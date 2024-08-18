import json
from collections import OrderedDict

from django.contrib.gis.gdal import GDALException
from django.contrib.gis.geos import GEOSException, GEOSGeometry
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import Field, SerializerMethodField

__all__ = ['GeometryField', 'GeometrySerializerMethodField']


class GeometryField(Field):
    """
    A field to handle GeoDjango Geometry fields
    """

    type_name = 'GeometryField'

    def __init__(
        self, precision=None, remove_duplicates=False, auto_bbox=False, **kwargs
    ):
        """
        :param auto_bbox: Whether the GeoJSON object should include a bounding box
        """
        self.precision = precision
        self.auto_bbox = auto_bbox
        self.remove_dupes = remove_duplicates
        super().__init__(**kwargs)
        self.style.setdefault('base_template', 'textarea.html')

    def to_representation(self, value):
        if isinstance(value, dict) or value is None:
            return value
        # we expect value to be a GEOSGeometry instance
        if value.geojson:
            geojson = GeoJsonDict(value.geojson)
        # in this case we're dealing with an empty point
        else:
            geojson = GeoJsonDict({'type': value.geom_type, 'coordinates': []})
        if geojson['type'] == 'GeometryCollection':
            geometries = geojson.get('geometries')
        else:
            geometries = [geojson]
        for geometry in geometries:
            if self.precision is not None:
                geometry['coordinates'] = self._recursive_round(
                    geometry['coordinates'], self.precision
                )
            if self.remove_dupes:
                geometry['coordinates'] = self._rm_redundant_points(
                    geometry['coordinates'], geometry['type']
                )
        if self.auto_bbox:
            geojson["bbox"] = value.extent
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
        except GEOSException:
            raise ValidationError(
                _(
                    'Invalid format: string or unicode input unrecognized as GeoJSON, WKT EWKT or HEXEWKB.'
                )
            )
        except (ValueError, TypeError, GDALException) as e:
            raise ValidationError(
                _('Unable to convert to python object: {}'.format(str(e)))
            )

    def validate_empty_values(self, data):
        if data == '':
            self.fail('required')
        return super().validate_empty_values(data)

    def _recursive_round(self, value, precision):
        """
        Round all numbers within an array or nested arrays
            value: number or nested array of numbers
            precision: integer valueue of number of decimals to keep
        """
        if hasattr(value, '__iter__'):
            return tuple(self._recursive_round(v, precision) for v in value)
        return round(value, precision)

    def _rm_redundant_points(self, geometry, geo_type):
        """
        Remove redundant coordinate pairs from geometry
            geometry: array of coordinates or nested-array of coordinates
            geo_type: GeoJSON type attribute for provided geometry, used to
                     determine structure of provided `geometry` argument
        """
        if geo_type in ('MultiPoint', 'LineString'):
            close = geo_type == 'LineString'
            output = []
            for coord in geometry:
                coord = tuple(coord)
                if not output or coord != output[-1]:
                    output.append(coord)
            if close and len(output) == 1:
                output.append(output[0])
            return tuple(output)
        if geo_type in ('MultiLineString', 'Polygon'):
            return [self._rm_redundant_points(c, 'LineString') for c in geometry]
        if geo_type == 'MultiPolygon':
            return [self._rm_redundant_points(c, 'Polygon') for c in geometry]
        return geometry


class GeometrySerializerMethodField(SerializerMethodField):
    def to_representation(self, value):
        value = super().to_representation(value)
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
        if args and isinstance(args[0], str):
            try:
                geojson = json.loads(args[0])
                args = (geojson,)
            except ValueError:
                pass
        super().__init__(*args, **kwargs)

    def __str__(self):
        """
        Avoid displaying strings like
        ``{ 'type': u'Point', 'coordinates': [12, 32] }``
        in DRF browsable UI inputs (python 2.6/2.7)
        see: https://github.com/openwisp/django-rest-framework-gis/pull/60
        """
        return json.dumps(self)
