# rest_framework_gis/fields.py

import json

from django.contrib.gis.geos import GEOSGeometry

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
        except ValueError:
            pass
        return value