from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.geos import Polygon

from rest_framework.serializers import ModelSerializer, ListSerializer, LIST_SERIALIZER_KWARGS

from .fields import GeometryField, GeometrySerializerMethodField  # noqa
from .utils import OrderedDict


class GeoModelSerializer(ModelSerializer):
    """
    Deprecated, will be removed in django-rest-framework-gis 1.0
    """


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

    def to_representation(self, instance):
        """
        Serialize objects -> primitives.
        """
        # prepare OrderedDict geojson structure
        feature = OrderedDict()
        # the list of fields that will be processed by get_properties
        # we will remove fields that have been already processed
        # to increase performance on large numbers
        fields = list(self.fields.values())

        # optional id attribute
        if self.Meta.id_field:
            field = self.fields[self.Meta.id_field]
            value = field.get_attribute(instance)
            feature["id"] = field.to_representation(value)
            fields.remove(field)

        # required type attribute
        # must be "Feature" according to GeoJSON spec
        feature["type"] = "Feature"

        # required geometry attribute
        # MUST be present in output according to GeoJSON spec
        field = self.fields[self.Meta.geo_field]
        geo_value = field.get_attribute(instance)
        feature["geometry"] = field.to_representation(geo_value)
        fields.remove(field)
        # Bounding Box
        # if auto_bbox feature is enabled
        # bbox will be determined automatically automatically
        if self.Meta.auto_bbox and geo_value:
            feature["bbox"] = geo_value.extent
        # otherwise it can be determined via another field
        elif self.Meta.bbox_geo_field:
            field = self.fields[self.Meta.bbox_geo_field]
            value = field.get_attribute(instance)
            feature["bbox"] = value.extent if hasattr(value, 'extent') else None
            fields.remove(field)

        # GeoJSON properties
        feature["properties"] = self.get_properties(instance, fields)

        return feature

    def get_properties(self, instance, fields):
        """
        Get the feature metadata which will be used for the GeoJSON
        "properties" key.

        By default it returns all serializer fields excluding those used for
        the ID, the geometry and the bounding box.

        :param instance: The current Django model instance
        :param fields: The list of fields to process (fields already processed have been removed)
        :return: OrderedDict containing the properties of the current feature
        :rtype: OrderedDict
        """
        properties = OrderedDict()

        for field in fields:
            if field.write_only:
                continue
            value = field.get_attribute(instance)
            properties[field.field_name] = field.to_representation(value)

        return properties

    def to_internal_value(self, data):
        """
        Override the parent method to first remove the GeoJSON formatting
        """
        if 'properties' in data:
            data = self.unformat_geojson(data)
        return super(GeoFeatureModelSerializer, self).to_internal_value(data)

    def unformat_geojson(self, feature):
        """
        This function should return a dictionary containing keys which maps
        to serializer fields.

        Remember that GeoJSON contains a key "properties" which contains the
        feature metadata. This should be flattened to make sure this
        metadata is stored in the right serializer fields.

        :param feature: The dictionary containing the feature data directly
                        from the GeoJSON data.
        :return: A new dictionary which maps the GeoJSON values to
                 serializer fields
        """
        attrs = feature["properties"]

        if 'geometry' in feature:
            attrs[self.Meta.geo_field] = feature['geometry']

        if self.Meta.bbox_geo_field and 'bbox' in feature:
            attrs[self.Meta.bbox_geo_field] = Polygon.from_bbox(feature['bbox'])

        return attrs
