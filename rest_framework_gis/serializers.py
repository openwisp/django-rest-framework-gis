from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.db.models.fields import GeometryField as django_GeometryField

from rest_framework.serializers import ModelSerializer, ListSerializer, LIST_SERIALIZER_KWARGS
from rest_framework.utils.field_mapping import ClassLookupDict

try:
    from collections import OrderedDict
# python 2.6
except ImportError:
    from ordereddict import OrderedDict

from .fields import GeometryField

# map drf-gis GeometryField to GeoDjango Geometry Field
try:
    _geo_field_mapping = ModelSerializer._field_mapping.mapping
except AttributeError:
    _geo_field_mapping = ModelSerializer.serializer_field_mapping
_geo_field_mapping.update({
    django_GeometryField: GeometryField
})


class GeoModelSerializer(ModelSerializer):
    """
    A subclass of DFR ModelSerializer that adds support
    for GeoDjango fields to be serialized as GeoJSON
    compatible data
    """
    _field_mapping = ClassLookupDict(_geo_field_mapping)


class GeoFeatureModelListSerializer(ListSerializer):
    @property
    def data(self):
        return super(ListSerializer, self).data

    def to_representation(self, data):
        """
        Add GeoJSON compatible formatting to a serialized queryset list
        """
        return OrderedDict((
            ("type", "FeatureCollection"),
            ("features", super(GeoFeatureModelListSerializer, self).to_representation(data))
        ))


class GeoFeatureModelSerializer(GeoModelSerializer):
    """
    A subclass of GeoModelSerializer
    that outputs geojson-ready data as
    features and feature collections
    """
    @classmethod
    def many_init(cls, *args, **kwargs):
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {'child': child_serializer}
        list_kwargs.update(dict([
            (key, value) for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        ]))
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', GeoFeatureModelListSerializer)
        return list_serializer_class(*args, **list_kwargs)

    def __init__(self, *args, **kwargs):
        super(GeoFeatureModelSerializer, self).__init__(*args, **kwargs)
        self.Meta.id_field = getattr(self.Meta, 'id_field', self.Meta.model._meta.pk.name)
        if self.Meta.geo_field is None:
            raise ImproperlyConfigured("You must define a 'geo_field'.")
        # make sure geo_field is included in fields
        if hasattr(self.Meta, 'exclude'):
            if self.Meta.geo_field in self.Meta.exclude:
                raise ImproperlyConfigured("You cannot exclude your 'geo_field'.")
        if hasattr(self.Meta, 'fields'):
            if self.Meta.geo_field not in self.Meta.fields:
                if type(self.Meta.fields) is tuple:
                    additional_fields = (self.Meta.geo_field, )
                else:
                    additional_fields = [self.Meta.geo_field, ]
                self.Meta.fields += additional_fields

    def to_representation(self, instance):
        """
        Serialize objects -> primitives.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        # geo structure
        if self.Meta.id_field is not False:
            ret["id"] = ""
        ret["type"] = "Feature"
        ret["geometry"] = {}
        ret["properties"] = OrderedDict()

        for field in fields:
            field_name = field.field_name
            if field.read_only and instance is None:
                continue
            value = field.get_attribute(instance)
            if value:
                value = field.to_representation(value)
            if self.Meta.id_field is not False and field_name == self.Meta.id_field:
                ret["id"] = value
            elif field_name == self.Meta.geo_field:
                ret["geometry"] = value
            elif not getattr(field, 'write_only', False):
                ret["properties"][field_name] = value

        return ret

    def to_internal_value(self, data):
        """
        Override the parent method to first remove the GeoJSON formatting
        """
        if 'features' in data:
            _unformatted_data = []
            features = data['features']
            for feature in features:
                _dict = feature["properties"]
                if 'geometry' in feature:
                    geom = { self.Meta.geo_field: feature["geometry"] }
                    _dict.update(geom)
                _unformatted_data.append(_dict)
        elif 'properties' in data:
            _dict = data["properties"]
            if 'geometry' in data:
                geom = { self.Meta.geo_field: data["geometry"] }
                _dict.update(geom)
            _unformatted_data = _dict
        else:
            _unformatted_data = data

        return super(GeoFeatureModelSerializer, self).to_internal_value(_unformatted_data)
