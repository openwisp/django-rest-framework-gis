import json

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import OGRException
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
        return JsonDict(GEOSGeometry(value).geojson)

    def to_internal_value(self, value):
        if value == '' or value is None:
            return value
        if isinstance(value, GEOSGeometry):
            # value already has the correct representation
            return value
        if isinstance(value, dict):
            value = json.dumps(value)
        try:
            return GEOSGeometry(value).geojson
        except (ValueError, GEOSException, OGRException, TypeError):
            raise ValidationError(_('Invalid format: string or unicode input unrecognized as WKT EWKT, and HEXEWKB.'))

    def validate_empty_values(self, data):
        if data == '':
            self.fail('required')
        return super(GeometryField, self).validate_empty_values(data)


class GeometrySerializerMethodField(SerializerMethodField):
    def to_representation(self, value):
        value = super(GeometrySerializerMethodField, self).to_representation(value)
        return JsonDict(GEOSGeometry(value).geojson)


class JsonDict(dict):
    """
    Takes GeoDjango geojson in input and converts it _back_ to a Python object
    Retains the geojson string for python 2,
    see: https://github.com/djangonauts/django-rest-framework-gis/pull/60

    TODO: remove this when python 2 will be deprecated
    """
    def __init__(self, data):
        self._geojson_string = data
        super(JsonDict, self).__init__(json.loads(data))

    def __str__(self):
        return self._geojson_string
