import json
import warnings

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

        try:
            geojson_value = getattr(self.parent.instance, '%s_geojson' % self.field_name)
            if geojson_value is not None:
                return GeoJSON(geojson_value)
            return None
        except AttributeError:
            warnings.warn(
                "`{0}`'s `{1}` field is missing its `{1}_geojson` field with "
                "raw JSON string from the database. This negatively impacts the performance "
                "of JSON rendering.".format(self.parent.instance, self.field_name),
                RuntimeWarning
            )

            # we expect value to be a GEOSGeometry instance
            return GeoJSON(value.geojson)

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
        except (ValueError, GEOSException, OGRException, TypeError):
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
            return GeoJSON(value.geojson)
        else:
            return None


class GeoJSON(object):
    __slots__ = ('json',)

    def __init__(self, json):
        self.json = json

    def __json__(self):
        return self.json

    def __str__(self):
        """
        Avoid displaying strings like
        ``{ 'type': u'Point', 'coordinates': [12, 32] }``
        in DRF browsable UI inputs (python 2.6/2.7)
        see: https://github.com/djangonauts/django-rest-framework-gis/pull/60
        """
        return self.json

    # GeoJSON contains a JSON string. If we are not using UJSONRenderer
    # to render data, then we have to parse that JSON string into an
    # object to make default JSON rendered render it again. We use the
    # fact that default encoder_class checks for tolist method and calls
    # it if it exists. All this conversion to object and back is not
    # performant, but we are optimizing for UJSONRenderer and not the
    # default JSONRenderer. But we still want to keep compatibility with it.
    def tolist(self):
        return json.loads(self.json)
