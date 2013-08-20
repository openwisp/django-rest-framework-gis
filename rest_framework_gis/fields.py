# rest_framework_gis/fields.py

try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.gis.geos import GEOSGeometry
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
        try:
            value = GEOSGeometry(json.dumps(value))
        except ValueError as e:
            raise ValidationError(_('Bad Format for GeoJSON field. %s' % e.message))
        # TODO: this is not ok, needs testing
        # validation error must be raised only if both json decoding and geos decoding fail
        return value