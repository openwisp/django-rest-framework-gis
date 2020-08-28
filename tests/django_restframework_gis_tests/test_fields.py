import json

from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from rest_framework import serializers

from rest_framework_gis import serializers as gis_serializers

Point = {"type": "Point", "coordinates": [-105.0162, 39.5742]}

MultiPoint = {
    "type": "MultiPoint",
    "coordinates": [
        [-105.0162, 39.5742],
        [-80.6665, 35.0539],
        [-80.6665, 35.0539],  # Dupe
        [-80.672, 35.049],
    ],
}

LineString = {
    "type": "LineString",
    "coordinates": [
        [-101.7443, 39.3215],
        [-101.4021, 39.3300],
        [-101.4038, 39.3300],
        [-101.4038, 39.3300],  # Dupe
        [-97.6354, 38.8739],
    ],
}

MultiLineString = {
    "type": "MultiLineString",
    "coordinates": [
        [
            [-105.0214, 39.5780],
            [-105.0215, 39.5778],
            [-105.0215, 39.5774],
            [-105.0215, 39.5771],
            [-105.0215, 39.5771],  # Dupe
            [-105.0215, 39.5770],
            [-105.0215, 39.5767],
        ],
        [
            [-105.0171, 39.5744],
            [-105.0169, 39.5743],
            [-105.0166, 39.5743],
            [-105.0166, 39.5743],  # Dupe
            [-105.0165, 39.5744],
            [-105.0159, 39.5742],
        ],
    ],
}

Polygon = {
    "type": "Polygon",
    "coordinates": [
        [
            [-84.3228, 34.9895],
            [-82.6062, 36.0335],
            [-82.6062, 35.9913],
            [-82.6062, 35.9791],
            [-82.5787, 35.9613],
            [-82.5787, 35.9613],  # Dupe
            [-82.5677, 35.9513],
            [-84.2211, 34.9850],
            [-84.3228, 34.9895],
        ],
        [
            [-75.6903, 35.7420],
            [-75.5914, 35.7420],
            [-75.5914, 35.7420],  # Dupe
            [-75.7067, 35.7420],
            [-75.6903, 35.7420],
        ],
    ],
}

MultiPolygon = {
    "type": "MultiPolygon",
    "coordinates": [
        [
            [
                [-84.3228, 34.9895],
                [-84.3227, 34.9895],
                [-84.3227, 34.9895],  # Dupe
                [-84.2211, 34.9850],
                [-84.3228, 34.9895],
            ],
            [
                [-75.6903, 35.7420],
                [-75.5913, 35.7420],
                [-75.5913, 35.7420],  # Dupe
                [-75.5914, 35.7420],
                [-75.6903, 35.7420],
            ],
        ],
        [
            [
                [-109.0283, 36.9850],
                [-102.0629, 40.9798],
                [-102.0629, 40.9798],  # Dupe
                [-109.0283, 36.9851],
                [-109.0283, 36.9850],
            ],
        ],
    ],
}

GeometryCollection = {
    "type": "GeometryCollection",
    "geometries": [Point, Polygon, LineString],
}


class BaseTestCase(TestCase):
    @staticmethod
    def get_instance(data_dict):
        class Model(object):
            def __init__(self, geojson_dict):
                self.geometry = GEOSGeometry(json.dumps(geojson_dict))

        return Model(data_dict)

    @staticmethod
    def create_serializer(**kwargs):
        class LocationGeoSerializer(serializers.Serializer):
            geometry = gis_serializers.GeometryField(**kwargs)

        return LocationGeoSerializer

    def normalize(self, data):
        """
        To help with equality operators, cast nested inputted data from
        OrderedDict or GeoJsonDict to dict and from tuple to array.
        """
        if isinstance(data, (tuple, list)):
            return [self.normalize(d) for d in data]
        if isinstance(data, dict):
            return {k: self.normalize(v) for k, v in data.items()}
        return data


class TestPrecision(BaseTestCase):
    def test_precision_Point(self):
        model = self.get_instance(Point)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {'geometry': {"type": "Point", "coordinates": [-105.02, 39.57]}},
        )

    def test_precision_MultiPoint(self):
        model = self.get_instance(MultiPoint)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "MultiPoint",
                    "coordinates": [
                        [-105.02, 39.57],
                        [-80.67, 35.05],
                        [-80.67, 35.05],
                        [-80.67, 35.05],
                    ],
                }
            },
        )

    def test_precision_LineString(self):
        model = self.get_instance(LineString)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "LineString",
                    "coordinates": [
                        [-101.74, 39.32],
                        [-101.40, 39.33],
                        [-101.40, 39.33],
                        [-101.40, 39.33],
                        [-97.64, 38.87],
                    ],
                }
            },
        )

    def test_precision_MultiLineString(self):
        model = self.get_instance(MultiLineString)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "MultiLineString",
                    "coordinates": [
                        [
                            [-105.02, 39.58],
                            [-105.02, 39.58],
                            [-105.02, 39.58],
                            [-105.02, 39.58],
                            [-105.02, 39.58],
                            [-105.02, 39.58],
                            [-105.02, 39.58],
                        ],
                        [
                            [-105.02, 39.57],
                            [-105.02, 39.57],
                            [-105.02, 39.57],
                            [-105.02, 39.57],
                            [-105.02, 39.57],
                            [-105.02, 39.57],
                        ],
                    ],
                }
            },
        )

    def test_precision_Polygon(self):
        model = self.get_instance(Polygon)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-84.32, 34.99],
                            [-82.61, 36.03],
                            [-82.61, 35.99],
                            [-82.61, 35.98],
                            [-82.58, 35.96],
                            [-82.58, 35.96],
                            [-82.57, 35.95],
                            [-84.22, 34.98],
                            [-84.32, 34.99],
                        ],
                        [
                            [-75.69, 35.74],
                            [-75.59, 35.74],
                            [-75.59, 35.74],
                            [-75.71, 35.74],
                            [-75.69, 35.74],
                        ],
                    ],
                }
            },
        )

    def test_precision_MultiPolygon(self):
        model = self.get_instance(MultiPolygon)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data

        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-84.32, 34.99],
                                [-84.32, 34.99],
                                [-84.32, 34.99],
                                [-84.22, 34.98],
                                [-84.32, 34.99],
                            ],
                            [
                                [-75.69, 35.74],
                                [-75.59, 35.74],
                                [-75.59, 35.74],
                                [-75.59, 35.74],
                                [-75.69, 35.74],
                            ],
                        ],
                        [
                            [
                                [-109.03, 36.98],
                                [-102.06, 40.98],
                                [-102.06, 40.98],
                                [-109.03, 36.99],
                                [-109.03, 36.98],
                            ],
                        ],
                    ],
                }
            },
        )

    def test_precision_GeometryCollection(self):
        model = self.get_instance(GeometryCollection)
        Serializer = self.create_serializer(precision=2)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                "geometry": {
                    "type": "GeometryCollection",
                    "geometries": [
                        {"type": "Point", "coordinates": [-105.02, 39.57]},
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-84.32, 34.99],
                                    [-82.61, 36.03],
                                    [-82.61, 35.99],
                                    [-82.61, 35.98],
                                    [-82.58, 35.96],
                                    [-82.58, 35.96],
                                    [-82.57, 35.95],
                                    [-84.22, 34.98],
                                    [-84.32, 34.99],
                                ],
                                [
                                    [-75.69, 35.74],
                                    [-75.59, 35.74],
                                    [-75.59, 35.74],
                                    [-75.71, 35.74],
                                    [-75.69, 35.74],
                                ],
                            ],
                        },
                        {
                            "type": "LineString",
                            "coordinates": [
                                [-101.74, 39.32],
                                [-101.4, 39.33],
                                [-101.4, 39.33],
                                [-101.4, 39.33],
                                [-97.64, 38.87],
                            ],
                        },
                    ],
                }
            },
        )


class TestRmRedundant(BaseTestCase):
    def test_rm_redundant_Point(self):
        model = self.get_instance({"type": "Point", "coordinates": [-1.1, -1.1]})
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {"geometry": {"type": "Point", "coordinates": [-1.1, -1.1]}},
        )

    def test_rm_redundant_MultiPoint(self):
        model = self.get_instance(MultiPoint)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                "geometry": {
                    "type": "MultiPoint",
                    "coordinates": [
                        [-105.0162, 39.5742],
                        [-80.6665, 35.0539],
                        # [-80.6665, 35.0539],  # Dupe
                        [-80.672, 35.049],
                    ],
                }
            },
        )

    def test_rm_redundant_LineString(self):
        model = self.get_instance(LineString)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-101.7443, 39.3215],
                        [-101.4021, 39.3300],
                        [-101.4038, 39.3300],
                        # [-101.4038, 39.3300],  # Dupe
                        [-97.6354, 38.8739],
                    ],
                }
            },
        )

    def test_rm_redundant_MultiLineString(self):
        model = self.get_instance(MultiLineString)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [
                        [
                            [-105.0214, 39.5780],
                            [-105.0215, 39.5778],
                            [-105.0215, 39.5774],
                            [-105.0215, 39.5771],
                            # [-105.0215, 39.5771],  # Dupe
                            [-105.0215, 39.5770],
                            [-105.0215, 39.5767],
                        ],
                        [
                            [-105.0171, 39.5744],
                            [-105.0169, 39.5743],
                            [-105.0166, 39.5743],
                            # [-105.0166, 39.5743],  # Dupe
                            [-105.0165, 39.5744],
                            [-105.0159, 39.5742],
                        ],
                    ],
                }
            },
        )

    def test_rm_redundant_Polygon(self):
        model = self.get_instance(Polygon)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-84.3228, 34.9895],
                            [-82.6062, 36.0335],
                            [-82.6062, 35.9913],
                            [-82.6062, 35.9791],
                            [-82.5787, 35.9613],
                            # [-82.5787, 35.9613],  # Dupe
                            [-82.5677, 35.9513],
                            [-84.2211, 34.985],
                            [-84.3228, 34.9895],
                        ],
                        [
                            [-75.6903, 35.742],
                            [-75.5914, 35.742],
                            # [-75.5914, 35.7420],  # Dupe
                            [-75.7067, 35.742],
                            [-75.6903, 35.742],
                        ],
                    ],
                }
            },
        )

    def test_rm_redundant_MultiPolygon(self):
        model = self.get_instance(MultiPolygon)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-84.3228, 34.9895],
                                [-84.3227, 34.9895],
                                # [-84.3227, 34.9895],  # Dupe
                                [-84.2211, 34.9850],
                                [-84.3228, 34.9895],
                            ],
                            [
                                [-75.6903, 35.7420],
                                [-75.5913, 35.7420],
                                # [-75.5913, 35.7420],  # Dupe
                                [-75.5914, 35.7420],
                                [-75.6903, 35.7420],
                            ],
                        ],
                        [
                            [
                                [-109.0283, 36.9850],
                                [-102.0629, 40.9798],
                                # [-102.0629, 40.9798],  # Dupe
                                [-109.0283, 36.9851],
                                [-109.0283, 36.9850],
                            ],
                        ],
                    ],
                }
            },
        )

    def test_rm_redundant_MultiPolygon_single_polygon(self):
        MultiPolygon = {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-109.17227935791, 45.0041122436525],
                        [-109.218215942383, 45.0039901733398],
                        [-109.218215942383, 45.0039901733398],
                        [-109.175567626953, 45.0041999816896],
                        [-109.17227935791, 45.0041122436525],
                    ]
                ]
            ],
        }
        model = self.get_instance(MultiPolygon)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                'geometry': {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-109.17227935791, 45.0041122436525],
                                [-109.218215942383, 45.0039901733398],
                                # [-109.218215942383, 45.0039901733398],  # Dupe
                                [-109.175567626953, 45.0041999816896],
                                [-109.17227935791, 45.0041122436525],
                            ]
                        ]
                    ],
                }
            },
        )

    def test_rm_redundant_GeometryCollection(self):
        model = self.get_instance(GeometryCollection)
        Serializer = self.create_serializer(remove_duplicates=True)
        data = Serializer(model).data
        self.assertEqual(
            self.normalize(data),
            {
                "geometry": {
                    "type": "GeometryCollection",
                    "geometries": [
                        {"type": "Point", "coordinates": [-105.0162, 39.5742]},
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-84.3228, 34.9895],
                                    [-82.6062, 36.0335],
                                    [-82.6062, 35.9913],
                                    [-82.6062, 35.9791],
                                    [-82.5787, 35.9613],
                                    # [-82.5787, 35.9613],  # Dupe
                                    [-82.5677, 35.9513],
                                    [-84.2211, 34.985],
                                    [-84.3228, 34.9895],
                                ],
                                [
                                    [-75.6903, 35.742],
                                    [-75.5914, 35.742],
                                    # [-75.5914, 35.7420],  # Dupe
                                    [-75.7067, 35.742],
                                    [-75.6903, 35.742],
                                ],
                            ],
                        },
                        {
                            "type": "LineString",
                            "coordinates": [
                                [-101.7443, 39.3215],
                                [-101.4021, 39.3300],
                                [-101.4038, 39.3300],
                                # [-101.4038, 39.3300],  # Dupe
                                [-97.6354, 38.8739],
                            ],
                        },
                    ],
                }
            },
        )
