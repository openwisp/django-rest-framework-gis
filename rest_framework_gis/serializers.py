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
            # if 'fields' are declared, make sure it includes 'geo_field'
            if self.opts.fields:
               if self.opts.geo_field not in self.opts.fields:
                   #self.opts.fields = list(self.opts.fields)
                   self.opts.fields.append(self.opts.geo_field)

    @property
	def data(self):
	    """
        Returns the serialized data on the serializer.
        """
        if self._data is None:
            obj = self.object

            if self.many is not None:
                many = self.many
            else:
                many = hasattr(obj, '__iter__') and not isinstance(obj, (Page, dict))
                if many:
                    warnings.warn('Implict list/queryset serialization is deprecated. '
                                  'Use the `many=True` flag when instantiating the serializer.',
                                  DeprecationWarning, stacklevel=2)

            if many:
                self._data = {}
                self._data["type"] = "FeatureCollection"
                self._data["features"] = [self.to_native(item) for item in obj]
            else:
                self._data = self.to_native(obj)

        return self._data

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
    	
    # TODO: from_native method


