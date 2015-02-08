# rest_framework_gis/fields.py

try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import OGRException
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import Field


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

        # Get GeoDjango geojson serialization and then convert it _back_ to
        # a Python object
        return json.loads(GEOSGeometry(value).geojson)

    def to_internal_value(self, value):
        if value == '' or value is None:
            return value

        if isinstance(value, dict):
            value = json.dumps(value)

        try:
            return GEOSGeometry(value).geojson
        except (ValueError, GEOSException, OGRException, TypeError):
            raise ValidationError(_('Invalid format: string or unicode input unrecognized as WKT EWKT, and HEXEWKB.'))

    def validate_empty_values(self, data):
        if data in [u'']:
            self.fail('required')
        return super(GeometryField, self).validate_empty_values(data)
