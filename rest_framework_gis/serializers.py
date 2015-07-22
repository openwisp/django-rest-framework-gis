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
        ret["properties"] = OrderedDict()
        if self.Meta.bbox_geo_field or self.Meta.auto_bbox:
            ret["bbox"] = None

        for field in self.fields.values():
            if field.write_only:
                continue

            field_name = field.field_name
            value = field.get_attribute(instance)
            value_repr = None

            if value is not None:
                if field_name == self.Meta.bbox_geo_field:
                    # check for GEOSGeometry specfifc properties to generate the extent
                    # of the geometry.
                    if hasattr(value, 'extent'):
                        value_repr = value.extent
                else:
                    value_repr = field.to_representation(value)

            if self.Meta.id_field is not False and field_name == self.Meta.id_field:
                ret["id"] = value_repr
            elif field_name == self.Meta.geo_field:
                ret["geometry"] = value_repr
                if self.Meta.auto_bbox and value:
                    ret['bbox'] = value.extent
            elif field_name == self.Meta.bbox_geo_field:
                ret["bbox"] = value_repr
            elif not getattr(field, 'write_only', False):
                ret["properties"][field_name] = value_repr
        return ret

    def to_internal_value(self, data):
        """
        Override the parent method to first remove the GeoJSON formatting
        """
        def make_unformated_data(feature):
            _dict = feature["properties"]
            if 'geometry' in feature:
                geom = {self.Meta.geo_field: feature["geometry"]}
                _dict.update(geom)
            if self.Meta.bbox_geo_field and 'bbox' in feature:
                # build a polygon from the bbox
                _dict.update({self.Meta.bbox_geo_field: Polygon.from_bbox(feature['bbox'])})
            return _dict

        if 'properties' in data:
            _unformatted_data = make_unformated_data(data)
        else:
            _unformatted_data = data

        return super(GeoFeatureModelSerializer, self).to_internal_value(_unformatted_data)
