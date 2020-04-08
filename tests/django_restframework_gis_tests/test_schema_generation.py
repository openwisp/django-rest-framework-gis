from django.test import RequestFactory, TestCase
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.schemas.openapi import SchemaGenerator

from rest_framework_gis.schema import GeoFeatureAutoSchema
from .serializers import *


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

        path = '/'
        method = 'GET'

        view = create_view(TestPointFieldView, 'POST', create_request('/'))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector._get_serializer(path, method)
        content = inspector._map_serializer(serializer)
        content.pop('type', None)
        content['properties']['properties'].pop('type', None)
        self.assertEqual(content, {
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['Feature']
                },
                'id': {
                    'type': 'integer',
                    'readOnly': True
                },
                'geometry': {
                    'type': 'object',
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['Point']
                        },
                        'coordinates': {
                            'type': 'array',
                            'items': {
                                'type': 'number',
                                'format': 'float'
                            },
                            'example': [12.9721, 77.5933],
                            'minItems': 2,
                            'maxItems': 3
                        }
                    }
                },
                'properties': {
                    'properties': {
                        'random_field1': {
                            'type': 'string',
                            'maxLength': 32
                        },
                        'random_field2': {
                            'type': 'integer',
                            'maximum': 2147483647,
                            'minimum': -2147483648
                        }
                    },
                    'required': ['random_field1', 'random_field2', 'location']
                }
            }
        })

    def test_point_field_inner_geo_serializer(self):
        class TestPointFieldView(RetrieveAPIView):
            serializer_class = ChildPointSerializer

        path = '/'
        method = 'GET'

        view = create_view(TestPointFieldView, 'POST', create_request('/'))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector._get_serializer(path, method)
        content = inspector._map_serializer(serializer)
        content.pop('type', None)
        content['properties']['point'].pop('type', None)
        content['properties']['point']['properties']['properties'].pop('type', None)
        self.assertEqual(content, {
            'properties': {
                'point': {
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['Feature']
                        },
                        'id': {
                            'type': 'integer',
                            'readOnly': True
                        },
                        'geometry': {
                            'type': 'object',
                            'properties': {
                                'type': {
                                    'type': 'string',
                                    'enum': ['Point']
                                },
                                'coordinates': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'number',
                                        'format': 'float'
                                    },
                                    'example': [12.9721, 77.5933],
                                    'minItems': 2,
                                    'maxItems': 3
                                }
                            }
                        },
                        'properties': {
                            'properties': {
                                'random_field1': {
                                    'type': 'string',
                                    'maxLength': 32
                                },
                                'random_field2': {
                                    'type': 'integer',
                                    'maximum': 2147483647,
                                    'minimum': -2147483648
                                }
                            },
                            'required': ['random_field1', 'random_field2', 'location']
                        }
                    }
                }
            },
            'required': [
                'point'
            ]
        })

    def test_point_field_inner_geo_list_serializer(self):
        class TestPointFieldView(RetrieveAPIView):
            serializer_class = ListChildPointSerializer

        path = '/'
        method = 'GET'

        view = create_view(TestPointFieldView, 'POST', create_request('/'))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector._get_serializer(path, method)
        content = inspector._map_serializer(serializer)
        content.pop('type', None)
        content['properties']['points'].pop('type', None)
        content['properties']['points']['properties']['features']['items']['properties']['properties'].pop('type', None)
        self.assertEqual(content, {
            'properties': {
                'points': {
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['FeatureCollection']
                        },
                        'features': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'type': {
                                        'type': 'string',
                                        'enum': ['Feature']
                                    },
                                    'id': {
                                        'type': 'integer',
                                        'readOnly': True
                                    },
                                    'geometry': {
                                        'type': 'object',
                                        'properties': {
                                            'type': {
                                                'type': 'string',
                                                'enum': ['Point']
                                            },
                                            'coordinates': {
                                                'type': 'array',
                                                'items': {
                                                    'type': 'number',
                                                    'format': 'float'
                                                },
                                                'example': [12.9721, 77.5933],
                                                'minItems': 2,
                                                'maxItems': 3
                                            }
                                        }
                                    },
                                    'properties': {
                                        'properties': {
                                            'random_field1': {
                                                'type': 'string',
                                                'maxLength': 32
                                            },
                                            'random_field2': {
                                                'type': 'integer',
                                                'maximum': 2147483647,
                                                'minimum': -2147483648
                                            }
                                        },
                                        'required': ['random_field1', 'random_field2', 'location']
                                    }
                                }
                            }
                        },
                    }
                }
            },
            'required': ['points']
        })

    def test_line_string_field(self):
        class TestLineStringFieldView(RetrieveAPIView):
            serializer_class = LineStringSerializer

        path = '/'
        method = 'GET'

        view = create_view(TestLineStringFieldView, 'POST', create_request('/'))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector._get_serializer(path, method)
        content = inspector._map_serializer(serializer)
        geometry_schema = content['properties']['geometry']
        geometry_schema.pop('type', None)
        self.assertEqual(geometry_schema, {
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['LineString']
                },
                'coordinates': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'number',
                            'format': 'float'
                        },
                        'example': [12.9721, 77.5933],
                        'minItems': 2,
                        'maxItems': 3
                    },
                    'example': [[22.4707, 70.0577], [12.9721, 77.5933]],
                    'minItems': 2
                }
            }
        })

    def test_polygon(self):
        class TestPolygonFieldView(RetrieveAPIView):
            serializer_class = PolygonSerializer

        path = '/'
        method = 'GET'

        view = create_view(TestPolygonFieldView, 'POST', create_request('/'))
        inspector = GeoFeatureAutoSchema()
        inspector.view = view
        serializer = inspector._get_serializer(path, method)
        content = inspector._map_serializer(serializer)
        geometry_schema = content['properties']['geometry']
        geometry_schema.pop('type', None)
        self.assertEqual(geometry_schema, {
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['Polygon']
                },
                'coordinates': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'number',
                                'format': 'float'
                            },
                            'example': [12.9721, 77.5933],
                            'minItems': 2,
                            'maxItems': 3
                        },
                        'example': [[22.4707, 70.0577], [12.9721, 77.5933]],
                        'minItems': 4
                    },
                    'example': [[0.0, 0.0], [0.0, 50.0], [50.0, 50.0], [50.0, 0.0], [0.0, 0.0]]
                }
            }
        })
