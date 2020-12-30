from unittest import SkipTest

import rest_framework
from django.test import RequestFactory, TestCase
from packaging import version
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.schemas.openapi import SchemaGenerator

from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.schema import GeoFeatureAutoSchema

from .serializers import (
    BoxedLocationGeoFeatureWithBBoxGeoFieldSerializer,
    ChildPointSerializer,
    GeometrySerializer,
    GeometrySerializerMethodFieldSerializer,
    LineStringSerializer,
    ListChildPointSerializer,
    MultiLineStringSerializer,
    MultiPointSerializer,
    MultiPolygonSerializer,
    PointSerializer,
)
from .views import (
    GeojsonBoxedLocationDetails,
    GeojsonLocationContainedInBBoxList,
    GeojsonLocationContainedInTileList,
    GeojsonLocationWithinDistanceOfPointList,
    geojson_location_list,
)

is_pre_drf_312 = version.parse(rest_framework.VERSION) < version.parse('3.12')

if is_pre_drf_312:
    raise SkipTest('Skip this test if DRF < 3.12')


def create_request(path):
    factory = RequestFactory()
    request = Request(factory.get(path))
    return request


def create_view(view_cls, method, request):
    generator = SchemaGenerator()
    view = generator.create_view(view_cls.as_view(), method, request)
    return view


class TestSchemaGeneration(TestCase):
    def test_point_field_outer_most_gis_serializer(self):
        class TestPointFieldView(RetrieveAPIView):
            serializer_class = PointSerializer

        path = "/"
        method = "GET"

        view = create_view(TestPointFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        content.pop("type", None)
        content["properties"]["properties"].pop("type", None)
        self.assertEqual(
            content,
            {
                "properties": {
                    "type": {"type": "string", "enum": ["Feature"]},
                    "id": {"type": "integer", "readOnly": True},
                    "geometry": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["Point"]},
                            "coordinates": {
                                "type": "array",
                                "items": {"type": "number", "format": "float"},
                                "example": [12.9721, 77.5933],
                                "minItems": 2,
                                "maxItems": 3,
                            },
                        },
                    },
                    "properties": {
                        "properties": {
                            "random_field1": {"type": "string", "maxLength": 32},
                            "random_field2": {
                                "type": "integer",
                                "maximum": 2147483647,
                                "minimum": -2147483648,
                            },
                        },
                        "required": ["random_field1", "random_field2", "location"],
                    },
                }
            },
        )

    def test_point_field_inner_geo_serializer(self):
        class TestPointFieldView(RetrieveAPIView):
            serializer_class = ChildPointSerializer

        path = "/"
        method = "GET"

        view = create_view(TestPointFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        content.pop("type", None)
        content["properties"]["point"].pop("type", None)
        content["properties"]["point"]["properties"]["properties"].pop("type", None)
        self.assertEqual(
            content,
            {
                "properties": {
                    "point": {
                        "properties": {
                            "type": {"type": "string", "enum": ["Feature"]},
                            "id": {"type": "integer", "readOnly": True},
                            "geometry": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["Point"]},
                                    "coordinates": {
                                        "type": "array",
                                        "items": {"type": "number", "format": "float"},
                                        "example": [12.9721, 77.5933],
                                        "minItems": 2,
                                        "maxItems": 3,
                                    },
                                },
                            },
                            "properties": {
                                "properties": {
                                    "random_field1": {
                                        "type": "string",
                                        "maxLength": 32,
                                    },
                                    "random_field2": {
                                        "type": "integer",
                                        "maximum": 2147483647,
                                        "minimum": -2147483648,
                                    },
                                },
                                "required": [
                                    "random_field1",
                                    "random_field2",
                                    "location",
                                ],
                            },
                        }
                    }
                },
                "required": ["point"],
            },
        )

    def test_point_field_inner_geo_list_serializer(self):
        class TestPointFieldView(RetrieveAPIView):
            serializer_class = ListChildPointSerializer

        path = "/"
        method = "GET"

        view = create_view(TestPointFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        content.pop("type", None)
        content["properties"]["points"].pop("type", None)
        content["properties"]["points"]["properties"]["features"]["items"][
            "properties"
        ]["properties"].pop("type", None)
        self.assertEqual(
            content,
            {
                "properties": {
                    "points": {
                        "properties": {
                            "type": {"type": "string", "enum": ["FeatureCollection"]},
                            "features": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["Feature"]},
                                        "id": {"type": "integer", "readOnly": True},
                                        "geometry": {
                                            "type": "object",
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "enum": ["Point"],
                                                },
                                                "coordinates": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "number",
                                                        "format": "float",
                                                    },
                                                    "example": [12.9721, 77.5933],
                                                    "minItems": 2,
                                                    "maxItems": 3,
                                                },
                                            },
                                        },
                                        "properties": {
                                            "properties": {
                                                "random_field1": {
                                                    "type": "string",
                                                    "maxLength": 32,
                                                },
                                                "random_field2": {
                                                    "type": "integer",
                                                    "maximum": 2147483647,
                                                    "minimum": -2147483648,
                                                },
                                            },
                                            "required": [
                                                "random_field1",
                                                "random_field2",
                                                "location",
                                            ],
                                        },
                                    },
                                },
                            },
                        }
                    }
                },
                "required": ["points"],
            },
        )

    def test_line_string_field(self):
        class TestLineStringFieldView(RetrieveAPIView):
            serializer_class = LineStringSerializer

        path = "/"
        method = "GET"

        view = create_view(TestLineStringFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        geometry_schema = content["properties"]["geometry"]
        geometry_schema.pop("type", None)
        self.assertEqual(
            geometry_schema,
            {
                "properties": {
                    "type": {"type": "string", "enum": ["LineString"]},
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number", "format": "float"},
                            "example": [12.9721, 77.5933],
                            "minItems": 2,
                            "maxItems": 3,
                        },
                        "example": [[22.4707, 70.0577], [12.9721, 77.5933]],
                        "minItems": 2,
                    },
                }
            },
        )

    def test_multi_polygon(self):
        class TestMultiPolygonFieldView(RetrieveAPIView):
            serializer_class = MultiPolygonSerializer

        path = "/"
        method = "GET"

        view = create_view(TestMultiPolygonFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        geometry_schema = content["properties"]["geometry"]
        geometry_schema.pop("type", None)
        self.assertEqual(
            geometry_schema,
            {
                "properties": {
                    "type": {"type": "string", "enum": ["MultiPolygon"]},
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number", "format": "float"},
                                    "example": [12.9721, 77.5933],
                                    "minItems": 2,
                                    "maxItems": 3,
                                },
                                "example": [[22.4707, 70.0577], [12.9721, 77.5933]],
                                "minItems": 4,
                            },
                            "example": [
                                [0.0, 0.0],
                                [0.0, 50.0],
                                [50.0, 50.0],
                                [50.0, 0.0],
                                [0.0, 0.0],
                            ],
                        },
                        "example": [
                            [
                                [0.0, 0.0],
                                [0.0, 50.0],
                                [50.0, 50.0],
                                [50.0, 0.0],
                                [0.0, 0.0],
                            ]
                        ],
                    },
                }
            },
        )

    def test_multi_line_string_field(self):
        class TestMultiLineStringFieldView(RetrieveAPIView):
            serializer_class = MultiLineStringSerializer

        path = "/"
        method = "GET"

        view = create_view(TestMultiLineStringFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        geometry_schema = content["properties"]["geometry"]
        geometry_schema.pop("type", None)
        self.assertEqual(
            geometry_schema,
            {
                "properties": {
                    "type": {"type": "string", "enum": ["MultiLineString"]},
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "number", "format": "float"},
                                "example": [12.9721, 77.5933],
                                "minItems": 2,
                                "maxItems": 3,
                            },
                            "example": [[22.4707, 70.0577], [12.9721, 77.5933]],
                            "minItems": 2,
                        },
                        "example": [[[22.4707, 70.0577], [12.9721, 77.5933]]],
                    },
                }
            },
        )

    def test_multi_point(self):
        class TestMultiLineStringFieldView(RetrieveAPIView):
            serializer_class = MultiPointSerializer

        path = "/"
        method = "GET"

        view = create_view(TestMultiLineStringFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        geometry_schema = content["properties"]["geometry"]
        geometry_schema.pop("type", None)
        self.assertEqual(
            geometry_schema,
            {
                "properties": {
                    "type": {"type": "string", "enum": ["MultiPoint"]},
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number", "format": "float"},
                            "example": [12.9721, 77.5933],
                            "minItems": 2,
                            "maxItems": 3,
                        },
                        "example": [[12.9721, 77.5933]],
                    },
                }
            },
        )

    def test_geometry_field(self):
        class GeometrySerializerFieldView(RetrieveAPIView):
            serializer_class = GeometrySerializer

        path = "/"
        method = "GET"

        view = create_view(GeometrySerializerFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        geometry_schema = content["properties"]["geometry"]
        geometry_schema.pop("type", None)
        geometry_schema['properties'].pop("coordinates", None)
        self.assertEqual(geometry_schema, {"properties": {"type": {"type": "string"}}})

    def check_bbox_schema(self):
        class TestMultiLineStringFieldView(RetrieveAPIView):
            serializer_class = MultiPointSerializer

        path = "/"
        method = "GET"

        view = create_view(TestMultiLineStringFieldView, "POST", create_request("/"))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        bbox_schema = content["properties"]["bbox"]
        self.assertEqual(
            bbox_schema,
            {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 4,
                "maxItems": 4,
                "example": [12.9721, 77.5933, 12.9721, 77.5933],
            },
        )

    def test_warning_for_geometry_serializer_method_field(self):
        class TestGeometrySerializerMethodField(RetrieveAPIView):
            serializer_class = GeometrySerializerMethodFieldSerializer

        path = "/"
        method = "GET"

        view = create_view(
            TestGeometrySerializerMethodField, "POST", create_request("/")
        )
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        with self.assertWarns(Warning):
            inspector.map_serializer(serializer)

    def test_schema_for_bbox_geo_field(self):
        path = "/"
        method = "GET"

        class GeojsonBoxedLocationDetailsWithBBoxGeoFieldView(
            GeojsonBoxedLocationDetails
        ):
            serializer_class = BoxedLocationGeoFeatureWithBBoxGeoFieldSerializer

        view = create_view(
            GeojsonBoxedLocationDetailsWithBBoxGeoFieldView, "GET", create_request("/")
        )
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector.get_serializer(path, method)
        content = inspector.map_serializer(serializer)
        bbox_schema = content["properties"]["bbox"]
        self.assertNotIn(
            "bbox_geometry", content["properties"]["properties"]["properties"]
        )
        self.assertEqual(
            bbox_schema,
            {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 4,
                "maxItems": 4,
                "example": [12.9721, 77.5933, 12.9721, 77.5933],
            },
        )


class TestPaginationSchemaGeneration(TestCase):
    def test_geo_json_pagination_schema(self):
        generated_schema = GeoJsonPagination().get_paginated_response_schema(
            geojson_location_list
        )
        self.assertIn("features", generated_schema["properties"])
        generated_schema["properties"].pop("features")
        self.assertDictEqual(
            generated_schema,
            {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["FeatureCollection"]},
                    "count": {"type": "integer", "example": 123},
                    "next": {
                        "type": "string",
                        "nullable": True,
                        "format": "uri",
                        "example": "http://api.example.org/accounts/?page=4",
                    },
                    "previous": {
                        "type": "string",
                        "nullable": True,
                        "format": "uri",
                        "example": "http://api.example.org/accounts/?page=2",
                    },
                },
            },
        )


class TestRestFrameworkGisFiltersSchema(TestCase):
    def test_in_BBox_filter_schema(self):
        path = "/"
        method = "GET"
        view = create_view(
            GeojsonLocationContainedInBBoxList, "GET", create_request("/")
        )
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        generated_schema = inspector.get_filter_parameters(path, method)
        self.assertDictEqual(
            generated_schema[0],
            {
                "name": "in_bbox",
                "required": False,
                "in": "query",
                "description": "Specify a bounding box as filter: in_bbox=min_lon,min_lat,max_lon,max_lat",
                "schema": {
                    "type": "array",
                    "items": {"type": "float"},
                    "minItems": 4,
                    "maxItems": 4,
                    "example": [0, 0, 10, 10],
                },
                "style": "form",
                "explode": False,
            },
        )

    def test_in_TMS_filter_schema(self):
        path = "/"
        method = "GET"
        view = create_view(
            GeojsonLocationContainedInTileList, "GET", create_request("/")
        )
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        generated_schema = inspector.get_filter_parameters(path, method)
        self.assertDictEqual(
            generated_schema[0],
            {
                "name": "tile",
                "required": False,
                "in": "query",
                "description": "Specify a bounding box filter defined by a TMS tile address: tile=Z/X/Y",
                "schema": {"type": "string", "example": "12/56/34"},
            },
        )

    def test_distance_to_point_filter(self):
        path = "/"
        method = "GET"
        view = create_view(
            GeojsonLocationWithinDistanceOfPointList, "GET", create_request("/")
        )
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        generated_schema = inspector.get_filter_parameters(path, method)
        self.assertListEqual(
            generated_schema,
            [
                {
                    "name": "dist",
                    "required": False,
                    "in": "query",
                    "schema": {"type": "number", "format": "float", "default": 1000},
                    "description": "Represents **Distance** in **Distance to point** filter. "
                    "Default value is used only if ***point*** is passed.",
                },
                {
                    "name": "point",
                    "required": False,
                    "in": "query",
                    "description": "Point represented in **x,y** format. "
                    "Represents **point** in **Distance to point filter**",
                    "schema": {
                        "type": "array",
                        "items": {"type": "float"},
                        "minItems": 2,
                        "maxItems": 2,
                        "example": [0, 10],
                    },
                    "style": "form",
                    "explode": False,
                },
            ],
        )
