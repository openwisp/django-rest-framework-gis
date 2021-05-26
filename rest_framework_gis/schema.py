import warnings

from django.contrib.gis.db import models
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.utils import model_meta

from rest_framework_gis.fields import GeometryField, GeometrySerializerMethodField
from rest_framework_gis.serializers import (
    GeoFeatureModelListSerializer,
    GeoFeatureModelSerializer,
)


class GeoFeatureAutoSchema(AutoSchema):
    COORDINATES_SCHEMA_FOR_POINT = {
        "type": "array",
        "items": {"type": "number", "format": "float"},
        "example": [12.9721, 77.5933],
        "minItems": 2,
        "maxItems": 3,
    }

    COORDINATES_SCHEMA_FOR_LINE_STRING = {
        "type": "array",
        "items": COORDINATES_SCHEMA_FOR_POINT,
        "example": [[22.4707, 70.0577], [12.9721, 77.5933]],
        "minItems": 2,
    }

    GEO_FIELD_TO_SCHEMA = {
        models.PointField: {
            "type": {"type": "string", "enum": ["Point"]},
            "coordinates": COORDINATES_SCHEMA_FOR_POINT,
        },
        models.LineStringField: {
            "type": {"type": "string", "enum": ["LineString"]},
            "coordinates": COORDINATES_SCHEMA_FOR_LINE_STRING,
        },
        models.PolygonField: {
            "type": {"type": "string", "enum": ["Polygon"]},
            "coordinates": {
                "type": "array",
                "items": {**COORDINATES_SCHEMA_FOR_LINE_STRING, "minItems": 4},
                "example": [
                    [0.0, 0.0],
                    [0.0, 50.0],
                    [50.0, 50.0],
                    [50.0, 0.0],
                    [0.0, 0.0],
                ],
            },
        },
    }

    GEO_FIELD_TO_SCHEMA[models.GeometryField] = {
        'type': {'type': 'string'},
        'coordinates': {
            'oneOf': [  # If you have custom subclass of GeometryField, Override `oneOf` property.
                GEO_FIELD_TO_SCHEMA[models.PointField],
                GEO_FIELD_TO_SCHEMA[models.LineStringField],
                GEO_FIELD_TO_SCHEMA[models.PolygonField],
            ],
            'example': GEO_FIELD_TO_SCHEMA[models.PolygonField]['coordinates'][
                'example'
            ],
        },
    }

    MULTI_FIELD_MAPPING = {
        models.PointField: models.MultiPointField,
        models.LineStringField: models.MultiLineStringField,
        models.PolygonField: models.MultiPolygonField,
        models.GeometryField: models.GeometryCollectionField,
    }

    for singular_field, multi_field in MULTI_FIELD_MAPPING.items():
        GEO_FIELD_TO_SCHEMA[multi_field] = {
            "type": {"type": "string", "enum": [multi_field.geom_class.__name__]},
            "coordinates": {
                "type": "array",
                "items": GEO_FIELD_TO_SCHEMA[singular_field]["coordinates"],
                "example": [
                    GEO_FIELD_TO_SCHEMA[singular_field]["coordinates"]["example"]
                ],
            },
        }

    def _map_geo_field(self, serializer, geo_field_name):
        field = serializer.fields[geo_field_name]
        if isinstance(field, GeometrySerializerMethodField):
            warnings.warn(
                "Geometry generation for GeometrySerializerMethodField is not supported."
            )
            return {}

        model_field_name = geo_field_name

        geo_field = model_meta.get_field_info(serializer.Meta.model).fields[
            model_field_name
        ]
        try:
            return self.GEO_FIELD_TO_SCHEMA[geo_field.__class__]
        except KeyError:
            warnings.warn(
                "Geometry generation for {field} is not supported.".format(field=field)
            )
            return {}

    def map_field(self, field):
        if isinstance(field, GeoFeatureModelListSerializer):
            return self._map_geo_feature_model_list_serializer(field)

        if isinstance(field, GeometryField):
            return {
                "type": "object",
                "properties": self._map_geo_field(field.parent, field.field_name),
            }

        return super().map_field(field)

    def _map_geo_feature_model_list_serializer(self, serializer):
        return {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["FeatureCollection"]},
                "features": {
                    "type": "array",
                    "items": self.map_serializer(serializer.child),
                },
            },
        }

    def _map_geo_feature_model_serializer(self, serializer):
        schema = super().map_serializer(serializer)

        geo_json_schema = {
            "type": "object",
            "properties": {"type": {"type": "string", "enum": ["Feature"]}},
        }

        if serializer.Meta.id_field:
            geo_json_schema["properties"]["id"] = schema["properties"].pop(
                serializer.Meta.id_field
            )

        geo_field = serializer.Meta.geo_field
        geo_json_schema["properties"]["geometry"] = {
            "type": "object",
            "properties": self._map_geo_field(serializer, geo_field),
        }
        schema["properties"].pop(geo_field)

        if serializer.Meta.auto_bbox or serializer.Meta.bbox_geo_field:
            geo_json_schema["properties"]["bbox"] = {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 4,
                "maxItems": 4,
                "example": [12.9721, 77.5933, 12.9721, 77.5933],
            }
            if serializer.Meta.bbox_geo_field in schema["properties"]:
                schema["properties"].pop(serializer.Meta.bbox_geo_field)

        geo_json_schema["properties"]["properties"] = schema

        return geo_json_schema

    def map_serializer(self, serializer):
        if isinstance(serializer, GeoFeatureModelListSerializer):
            return self._map_geo_feature_model_list_serializer(serializer)

        if isinstance(serializer, GeoFeatureModelSerializer):
            return self._map_geo_feature_model_serializer(serializer)

        return super().map_serializer(serializer)
