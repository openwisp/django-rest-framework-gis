# rest_framework_gis/serializers.py
from django.contrib.gis.db import models

from rest_framework.serializers import ModelSerializer

from .fields import GeometryField

class GeoModelSerializerOptions(ModelSerializerOptions):
    """
    Options for GeoModelSerializer
    """
    def __init__(self, meta):
        super(GeoModelSerializerOptions, self).__init__(meta)
        self.geo_field = getattr(meta, 'geo_field', None)

class GeoModelSerializer(ModelSerializer):
    """
    A subclass of ModelSerializer that outputs geojson-ready data
    """
    _options_class = GeoModelSerializerOptions


    def __init__(self, *args, **kwargs):
        super(HyperGeoModelSerializer, self).__init__(*args, **kwargs)
        if self.opts.geo_field is None:
            raise ImproperlyConfigured("You must define a 'geo_field'.")
        else:
            # TODO: make sure the geo_field is a GeoDjango geometry field
            pass

    def get_field(self, model_field):
        """
        Creates a default instance of a basic non-relational field.
        """
        kwargs = {}

        kwargs['blank'] = model_field.blank

        if model_field.null or model_field.blank:
            kwargs['required'] = False

        if isinstance(model_field, models.AutoField) or not model_field.editable:
            kwargs['read_only'] = True

        if model_field.has_default():
            kwargs['required'] = False
            kwargs['default'] = model_field.get_default()

        if issubclass(model_field.__class__, models.TextField):
            kwargs['widget'] = widgets.Textarea

        # TODO: TypedChoiceField?
        if model_field.flatchoices:  # This ModelField contains choices
            kwargs['choices'] = model_field.flatchoices
            return ChoiceField(**kwargs)

        field_mapping = {
            models.AutoField: IntegerField,
            models.FloatField: FloatField,
            models.IntegerField: IntegerField,
            models.PositiveIntegerField: IntegerField,
            models.SmallIntegerField: IntegerField,
            models.PositiveSmallIntegerField: IntegerField,
            models.DateTimeField: DateTimeField,
            models.EmailField: EmailField,
            models.CharField: CharField,
            models.URLField: URLField,
            models.SlugField: SlugField,
            models.TextField: CharField,
            models.CommaSeparatedIntegerField: CharField,
            models.BooleanField: BooleanField,
            models.FileField: FileField,
            models.ImageField: ImageField,
            models.GeometryField: GeometryField,
            models.PointField: GeometryField,
            models.LineStringField: GeometryField,
            models.PolygonField: GeometryField,
            models.MultiPointField: GeometryField,
            models.MultiLineStringField: GeometryField,
            models.MultiPolygonField: GeometryField,
            models.GeometryCollectionField: GeometryField
        }

        try:
            return field_mapping[model_field.__class__](**kwargs)
        except KeyError:
            return ModelField(model_field=model_field, **kwargs)
