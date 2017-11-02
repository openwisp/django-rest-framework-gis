import six  # TODO Remove this along with GeoJsonDict when support for python 2.6/2.7 is dropped.
import json
from collections import OrderedDict

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import GDALException
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import Field, SerializerMethodField


__all__ = ['GeometryField', 'GeometrySerializerMethodField']


class GeometryField(Field):
    """
    A field to handle GeoDjango Geometry fields
    """
    type_name = 'GeometryField'

    def __init__(self, **kwargs):
        super(GeometryField, self).__init__(**kwargs)
        self.style = {'base_template': 'textarea.html'}

    def to_representation(self, value):
        if isinstance(value, dict) or value is None:
            return value
        # we expect value to be a GEOSGeometry instance
        return GeoJsonDict(value.geojson)

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
        except (ValueError, GEOSException, GDALException, TypeError):
            raise ValidationError(_('Invalid format: string or unicode input unrecognized as GeoJSON, WKT EWKT or HEXEWKB.'))

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
