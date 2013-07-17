# rest_framework_gis/serializers.py
from django.contrib.gis.db import models

from rest_framework.serializers import ModelSerializer, ModelSerializerOptions

from .fields import GeometryField

class GeoModelSerializer(ModelSerializer):
    """
        A subclass of DFR ModelSerializer that adds support
        for GeoDjango fields to be serialized as GeoJSON
        compatible data
    """

    field_mapping = dict(ModelSerializer.field_mapping)
    field_mapping.update({
        models.GeometryField: GeometryField,
        models.PointField: GeometryField,
        models.LineStringField: GeometryField,
        models.PolygonField: GeometryField,
        models.MultiPointField: GeometryField,
        models.MultiLineStringField: GeometryField,
        models.MultiPolygonField: GeometryField,
        models.GeometryCollectionField: GeometryField
   })

class GeoFeatureModelSerializerOptions(ModelSerializerOptions):
    """
        Options for GeoFeatureModelSerializer
    """
    def __init__(self, meta):
        super(GeoFeatureModelSerializerOptions, self).__init__(meta)
        self.geo_field = getattr(meta, 'geo_field', None)

class GeoFeatureModelSerializer(GeoModelSerializer):
    """
         A subclass of GeoFeatureModelSerializer 
         that outputs geojson-ready data
    """
    _options_class = GeoFeatureModelSerializerOptions


    def __init__(self, *args, **kwargs):
        super(GeoFeatureModelSerializer, self).__init__(*args, **kwargs)
        if self.opts.geo_field is None:
            raise ImproperlyConfigured("You must define a 'geo_field'.")
        else:
            # TODO: make sure the geo_field is a GeoDjango geometry field
            pass

    def get_default_fields(self):
        """
           Make sure geo_field is always included in the result
        """
        fields = super(GeoFeatureModelSerializer, self).get_default_fields()

        #ret[geo_field.name] = geo_field
        #ret.update(fields)
        #fields = ret

        return fields



    # TODO: implement new to_native and from_native methods for
    #       input/output of properly formatted GeoJSON. 

    def to_native(self, obj):
        """
            Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}
        ret["type"] = "Feature" 
        ret["properties"] = {}
        ret["geometry"] = {}
        
        for field_name, field in self.fields.items():
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            if field_name == self.opts.geo_field:
                ret["geometry"] = value
            else:
                ret["properties"][key] = value
                ret.fields[key] = field
        return ret    	
    	
