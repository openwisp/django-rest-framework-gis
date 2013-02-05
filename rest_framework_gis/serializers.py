# rest_framework_gis/serializers.py
from django.db import models
from django.contrib.gis.db import models as geomodels

from rest_framework.serializers import ModelSerializer

from .fields import GeometryField

class GeoModelSerializer(ModelSerializer):
    
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
            geomodels.GeometryField: GeometryField,
            geomodels.PointField: GeometryField,
            geomodels.LineStringField: GeometryField,
            geomodels.PolygonField: GeometryField,
            geomodels.MultiPointField: GeometryField,
            geomodels.MultiLineStringField: GeometryField,
            geomodels.MultiPolygonField: GeometryField,
            geomodels.GeometryCollectionField: GeometryField
        }

        try:
            return field_mapping[model_field.__class__](**kwargs)
        except KeyError:
            return ModelField(model_field=model_field, **kwargs)
