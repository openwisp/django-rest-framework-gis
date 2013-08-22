# rest_framework_gis/fields.py

try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import OGRException
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework.fields import WritableField


class GeometryField(WritableField):
    """
    A field to handle GeoDjango Geometry fields
    """
    type_name = 'GeometryField'

    def to_native(self, value):
        if isinstance(value, dict) or value is None:
            return value

        # Get GeoDjango geojson serialization and then convert it _back_ to
        # a Python object
        return json.loads(value.geojson)

    def from_native(self, value):
        if value == '' or value is None:
            return value

        if isinstance(value, dict):
            value = json.dumps(value)

        try:
            return GEOSGeometry(value)
        except (ValueError, GEOSException, OGRException, TypeError) as e:
            raise ValidationError(_('Invalid format: string or unicode input unrecognized as WKT EWKT, and HEXEWKB.'))

        return value