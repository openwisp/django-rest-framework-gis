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
            # make sure geo_field is included in fields
            if self.opts.geo_field in self.opts.exclude:
                raise ImproperlyConfigured("You cannot exclude your 'geo_field'.")
            if self.opts.geo_field not in self.opts.fields:
                self.opts.fields = self.opts.fields + (self.opts.geo_field, )
                self.fields = self.get_fields()
            

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
 
    def _format_data(self):
        """
           Add GeoJSON compatible formatting to a serialized queryset list
        """
        _data = super(GeoFeatureModelSerializer, self).data
        if isinstance(_data, list):
            self._formatted_data = {}
            self._formatted_data["type"] = "FeatureCollection"
            self._formatted_data["features"] = _data
        else:
            self._formatted_data = _data

        return self._formatted_data
            

    @property
    def data(self):
        """
        Returns the serialized data on the serializer.
        """
        return self._format_data()


      	
    	
    # TODO: from_native method


