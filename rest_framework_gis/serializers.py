# rest_framework_gis/serializers.py
from django.contrib.gis.db import models

from rest_framework.serializers import ModelSerializer, ModelSerializerOptions

from .fields import GeometryField

class GeoModelSerializer(ModelSerializer):

    pass

GeoModelSerializer.field_mapping.update({
    models.GeometryField: GeometryField,
    models.PointField: GeometryField,
    models.LineStringField: GeometryField,
    models.PolygonField: GeometryField,
    models.MultiPointField: GeometryField,
    models.MultiLineStringField: GeometryField,
    models.MultiPolygonField: GeometryField,
    models.GeometryCollectionField: GeometryField
})

class GeoModelFeatureSerializerOptions(ModelSerializerOptions):
    """
    Options for GeoModelFeatureSerializer
    """
    def __init__(self, meta):
        super(GeoModelFeatureSerializerOptions, self).__init__(meta)
        self.geo_field = getattr(meta, 'geo_field', None)

class GeoModelFeatureSerializer(GeoModelSerializer):
    """
    A subclass of GeoModelSerializer that outputs geojson-ready data
    """
    _options_class = GeoModelFeatureSerializerOptions


    def __init__(self, *args, **kwargs):
        super(GeoModelFeatureSerializer, self).__init__(*args, **kwargs)
        if self.opts.geo_field is None:
            raise ImproperlyConfigured("You must define a 'geo_field'.")
        else:
            # TODO: make sure the geo_field is a GeoDjango geometry field
            pass

    # TODO: implement new to_native and from_native methods for
    #       input/output of properly formatted GeoJSON. 
