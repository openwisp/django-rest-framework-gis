from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.db.models.fields import GeometryField as django_GeometryField

from rest_framework.serializers import ModelSerializer, ModelSerializerOptions

from .fields import GeometryField


class MapGeometryField(dict):
    def __getitem__(self, key):
        if issubclass(key, django_GeometryField):
            return GeometryField
        return super(MapGeometryField, self).__getitem__(key)


class GeoModelSerializer(ModelSerializer):
    """
    A subclass of DFR ModelSerializer that adds support
    for GeoDjango fields to be serialized as GeoJSON
    compatible data
    """
    field_mapping = MapGeometryField(ModelSerializer.field_mapping)


class GeoFeatureModelSerializerOptions(ModelSerializerOptions):
    """
    Options for GeoFeatureModelSerializer
    """
    def __init__(self, meta):
        super(GeoFeatureModelSerializerOptions, self).__init__(meta)
        self.geo_field = getattr(meta, 'geo_field', None)
        # id field defaults to primary key of the model
        self.id_field = getattr(meta, 'id_field', meta.model._meta.pk.name)


class GeoFeatureModelSerializer(GeoModelSerializer):
    """
    A subclass of GeoModelSerializer 
    that outputs geojson-ready data as
    features and feature collections
    """
    _options_class = GeoFeatureModelSerializerOptions
    
    def __init__(self, *args, **kwargs):
        super(GeoFeatureModelSerializer, self).__init__(*args, **kwargs)
        if self.opts.geo_field is None:
            raise ImproperlyConfigured("You must define a 'geo_field'.")
        else:
            # TODO: make sure the geo_field is a GeoDjango geometry field
            # make sure geo_field is included in fields
            if self.opts.exclude:
                if self.opts.geo_field in self.opts.exclude:
                    raise ImproperlyConfigured("You cannot exclude your 'geo_field'.")
            if self.opts.fields:
                if self.opts.geo_field not in self.opts.fields:
                    self.opts.fields = self.opts.fields + (self.opts.geo_field, )
                    self.fields = self.get_fields()

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}
        
        # geo structure
        if self.opts.id_field is not False:
            ret["id"] = ""
        ret["type"] = "Feature"
        ret["geometry"] = {}
        ret["properties"] = self._dict_class()
        
        for field_name, field in self.fields.items():
            if field.read_only and obj is None:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            method = getattr(self, 'transform_%s' % field_name, None)
            if callable(method):
                value = method(obj, value)
            
            if self.opts.id_field is not False and field_name == self.opts.id_field:
                ret["id"] = value
            elif field_name == self.opts.geo_field:
                ret["geometry"] = value
            elif not getattr(field, 'write_only', False):
                ret["properties"][key] = value
            
            ret.fields[key] = self.augment_field(field, field_name, key, value)
        
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
    
    def from_native(self, data, files):
        """
        Override the parent method to first remove the GeoJSON formatting
        """
        self._errors = {}
        
        if data is not None or files is not None:
            if 'features' in data:
                _unformatted_data = []
                features = data['features']
                for feature in features:
                    _dict = feature["properties"]
                    geom = { self.opts.geo_field: feature["geometry"] }
                    _dict.update(geom)
                    _unformatted_data.append(_dict)
            elif 'properties' in data:
                _dict = data["properties"]
                geom = { self.opts.geo_field: data["geometry"] }
                _dict.update(geom)
                _unformatted_data = _dict
            else:
                _unformatted_data = data
            
            attrs = self.restore_fields(_unformatted_data, files)
            if attrs is not None:
                attrs = self.perform_validation(attrs)
        else:
            self._errors['non_field_errors'] = ['No input provided']
        
        if not self._errors:
            return self.restore_object(attrs, instance=getattr(self, 'object', None))
