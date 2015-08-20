from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.geos import Polygon

from rest_framework.serializers import ModelSerializer, ListSerializer, LIST_SERIALIZER_KWARGS

from .fields import GeometryField, GeometrySerializerMethodField  # noqa
from .utils import OrderedDict


class GeoModelSerializer(ModelSerializer):
    """
    Deprecated, will be removed in django-rest-framework-gis 1.0
    """
    def __init__(self, *args, **kwargs):  # pragma: no cover
        # TODO: remove in 1.0
        from .apps import AppConfig
        import warnings
        import rest_framework_gis
        AppConfig('rest_framework_gis', rest_framework_gis).ready()
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn('\nGeoModelSerializer is deprecated, '
                      'add "rest_framework_gis" to settings.INSTALLED_APPS and use '
                      '"rest_framework.ModelSerializer" instead',
                      DeprecationWarning)
        super(GeoModelSerializer, self).__init__(*args, **kwargs)


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


class GeoFeatureModelSerializer(ModelSerializer):
    """
    A subclass of ModelSerializer
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
        if not hasattr(self.Meta, 'geo_field') or not self.Meta.geo_field:
            raise ImproperlyConfigured("You must define a 'geo_field'.")

        def check_excludes(field_name, field_role):
            """make sure the field is not excluded"""
            if hasattr(self.Meta, 'exclude') and field_name in self.Meta.exclude:
                raise ImproperlyConfigured("You cannot exclude your '{0}'.".format(field_role))

        def add_to_fields(field_name):
            """Make sure the field is included in the fields"""
            if hasattr(self.Meta, 'fields'):
                if field_name not in self.Meta.fields:
                    if type(self.Meta.fields) is tuple:
                        additional_fields = (field_name,)
                    else:
                        additional_fields = [field_name]
                    self.Meta.fields += additional_fields

        check_excludes(self.Meta.geo_field, 'geo_field')
        add_to_fields(self.Meta.geo_field)

        self.Meta.bbox_geo_field = getattr(self.Meta, 'bbox_geo_field', None)
        if self.Meta.bbox_geo_field:
            check_excludes(self.Meta.bbox_geo_field, 'bbox_geo_field')
            add_to_fields(self.Meta.bbox_geo_field)

        self.Meta.auto_bbox = getattr(self.Meta, 'auto_bbox', False)
        if self.Meta.bbox_geo_field and self.Meta.auto_bbox:
            raise ImproperlyConfigured(
                "You must eiher define a 'bbox_geo_field' or 'auto_bbox', but you can not set both"
            )

    def postprocess_properties(self, properties):
        return properties

    def to_representation(self, instance):
        """
        Serialize objects -> primitives.
        """
        # prepare OrderedDict geojson structure
        ret = OrderedDict()
        if self.Meta.id_field is not False:
            ret["id"] = None
        ret["type"] = "Feature"
        ret["geometry"] = None
        if self.Meta.bbox_geo_field or self.Meta.auto_bbox:
            ret["bbox"] = None

        if not hasattr(self, 'geo_field'):
            self.geo_field = self.fields.pop(self.Meta.geo_field) if self.Meta.geo_field in self.fields else None

        if not hasattr(self, 'bbox_geo_field'):
            self.bbox_geo_field = self.fields.pop(self.Meta.bbox_geo_field) if self.Meta.bbox_geo_field in self.fields else None

        properties = super(GeoFeatureModelSerializer, self).to_representation(instance)

        if self.Meta.id_field in self.fields:
            ret['id'] = properties.pop(self.Meta.id_field)

        ret['properties'] = self.postprocess_properties(properties)

        if self.geo_field is not None and not self.geo_field.write_only:
            value = self.geo_field.get_attribute(instance)
            ret['geometry'] = self.geo_field.to_representation(value)
            if self.Meta.auto_bbox:
                ret['bbox'] = value.extent

        if self.bbox_geo_field is not None and not self.bbox_geo_field.write_only:
            value = self.bbox_geo_field.get_attribute(instance)
            if hasattr(value, 'extent'):
                ret['bbox'] = value.extent

        return ret

    def preprocess_properties(self, properties):
        return properties

    def to_internal_value(self, data):
        """
        Override the parent method to first remove the GeoJSON formatting
        """

        if 'properties' in data:
            _unformatted_data = self.preprocess_properties(data['properties'])
            if 'geometry' in data:
                _unformatted_data[self.Meta.geo_field] = data['geometry']

            if self.Meta.bbox_geo_field and 'bbox' in data:
                # build a polygon from the bbox
                _unformatted_data[self.Meta.bbox_geo_field] = Polygon.from_bbox(data['bbox'])
        else:
            _unformatted_data = data

        return super(GeoFeatureModelSerializer, self).to_internal_value(_unformatted_data)
