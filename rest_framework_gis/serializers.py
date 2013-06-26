# rest_framework_gis/serializers.py
from django.contrib.gis.db import models

from rest_framework.serializers import ModelSerializer

from .fields import GeometryField


class GeoModelSerializer(ModelSerializer):

    pass

GeoModelSerializer.field_mapping.update({
    models.GeometryField: GeometryField,
    models.PointField: GeometryField,
    models.LineStringField: GeometryField,
    models.PolygonField: GeometryField,
    models.MultiPointField: GeometryField,
    models.MultiLineStringField: GeometryField,
    models.MultiPolygonField: GeometryField,
    models.GeometryCollectionField: GeometryField
})
