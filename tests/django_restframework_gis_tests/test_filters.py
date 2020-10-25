import json
import urllib
from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from .models import Location
from .views import (
    GeojsonLocationContainedInBBoxList,
    GeojsonLocationOrderDistanceToPointList,
    GeojsonLocationWithinDistanceOfPointList,
)

has_spatialite = (
    settings.DATABASES['default']['ENGINE']
    == 'django.contrib.gis.db.backends.spatialite'
)

try:
    from django.contrib.gis.db.models.functions import GeometryDistance

    has_geometry_distance = GeometryDistance and True
except ImportError:
    has_geometry_distance = False


class TestRestFrameworkGisFilters(TestCase):
    """
    unit tests for filters feature in restframework_gis
    """

    def setUp(self):
        self.location_contained_in_bbox_list_url = reverse(
            'api_geojson_location_list_contained_in_bbox_filter'
        )
        self.location_overlaps_bbox_list_url = reverse(
            'api_geojson_location_list_overlaps_bbox_filter'
        )
        self.location_contained_in_tile_list_url = reverse(
            'api_geojson_location_list_contained_in_tile_filter'
        )
        self.location_overlaps_tile_list_url = reverse(
            'api_geojson_location_list_overlaps_tile_filter'
        )
        self.location_within_distance_of_point_list_url = reverse(
            'api_geojson_location_list_within_distance_of_point_filter'
        )
        self.location_within_degrees_of_point_list_url = reverse(
            'api_geojson_location_list_within_degrees_of_point_filter'
        )
        self.geojson_contained_in_geometry = reverse(
            'api_geojson_contained_in_geometry'
        )
        self.location_order_distance_to_point = reverse(
            'api_geojson_location_order_distance_to_point_list_filter'
        )

        treasure_island_geojson = """{
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -122.44640350341795,
                        37.86103094116189
                    ],
                    [
                        -122.44262695312501,
                        37.85506751416839
                    ],
                    [
                        -122.43481636047363,
                        37.853305500228025
                    ],
                    [
                        -122.42975234985352,
                        37.854660899304704
                    ],
                    [
                        -122.41953849792479,
                        37.852627791344894
                    ],
                    [
                        -122.41807937622069,
                        37.853305500228025
                    ],
                    [
                        -122.41868019104004,
                        37.86211514878027
                    ],
                    [
                        -122.42391586303711,
                        37.870584971740065
                    ],
                    [
                        -122.43035316467285,
                        37.8723465726078
                    ],
                    [
                        -122.43515968322752,
                        37.86963639998042
                    ],
                    [
                        -122.43953704833984,
                        37.86882332875222
                    ],
                    [
                        -122.44640350341795,
                        37.86103094116189
                    ]
                ]
            ]
        }"""
        self.treasure_island_geom = GEOSGeometry(treasure_island_geojson)

        ggpark_geojson = """{
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -122.5111198425293,
                        37.77125750792944
                    ],
                    [
                        -122.51026153564452,
                        37.76447260365713
                    ],
                    [
                        -122.45309829711913,
                        37.76677954095475
                    ],
                    [
                        -122.45481491088867,
                        37.77424266859531
                    ],
                    [
                        -122.5111198425293,
                        37.77125750792944
                    ]
                ]
            ]
        }"""
        self.ggpark_geom = GEOSGeometry(ggpark_geojson)

    def test_inBBOXFilter_filtering(self):
        """
        Checks that the inBBOXFilter returns only objects strictly contained
        in the bounding box given by the in_bbox URL parameter
        """
        self.assertEqual(Location.objects.count(), 0)

        # Bounding box
        xmin = 0
        ymin = 0
        xmax = 10
        ymax = 10

        url_params = '?in_bbox=%d,%d,%d,%d&format=json' % (xmin, ymin, xmax, ymax)

        # Square with bottom left at (1,1), top right at (9,9)
        isContained = Location()
        isContained.name = 'isContained'
        isContained.geometry = Polygon(((1, 1), (9, 1), (9, 9), (1, 9), (1, 1)))
        isContained.save()

        isEqualToBounds = Location()
        isEqualToBounds.name = 'isEqualToBounds'
        isEqualToBounds.geometry = Polygon(((0, 0), (10, 0), (10, 10), (0, 10), (0, 0)))
        isEqualToBounds.save()

        # Rectangle with bottom left at (-1,1), top right at (5,5)
        overlaps = Location()
        overlaps.name = 'overlaps'
        overlaps.geometry = Polygon(((-1, 1), (5, 1), (5, 5), (-1, 5), (-1, 1)))
        overlaps.save()

        # Rectangle with bottom left at (-3,-3), top right at (-1,2)
        nonIntersecting = Location()
        nonIntersecting.name = 'nonIntersecting'
        nonIntersecting.geometry = Polygon(
            ((-3, -3), (-1, -3), (-1, 2), (-3, 2), (-3, -3))
        )
        nonIntersecting.save()

        # Make sure we only get back the ones strictly contained in the bounding box
        response = self.client.get(
            self.location_contained_in_bbox_list_url + url_params
        )
        self.assertEqual(len(response.data['features']), 2)
        for result in response.data['features']:
            self.assertEqual(
                result['properties']['name'] in ('isContained', 'isEqualToBounds'), True
            )

        # Make sure we get overlapping results for the view which allows bounding box overlaps.
        response = self.client.get(self.location_overlaps_bbox_list_url + url_params)
        self.assertEqual(len(response.data['features']), 3)
        for result in response.data['features']:
            self.assertEqual(
                result['properties']['name']
                in ('isContained', 'isEqualToBounds', 'overlaps'),
                True,
            )

    @skipIf(has_spatialite, 'Skipped test for spatialite backend: not accurate enough')
    def test_TileFilter_filtering(self):
        """
        Checks that the TMSTileFilter returns only objects strictly contained
        in the bounding box given by the tile URL parameter
        """
        self.assertEqual(Location.objects.count(), 0)

        # Bounding box
        z = 1
        x = 1
        y = 0

        url_params = '?tile=%d/%d/%d&format=json' % (z, x, y)

        # Square with bottom left at (1,1), top right at (9,9)
        isContained = Location()
        isContained.name = 'isContained'
        isContained.geometry = Polygon(((1, 1), (9, 1), (9, 9), (1, 9), (1, 1)))
        isContained.save()

        isEqualToBounds = Location()
        isEqualToBounds.name = 'isEqualToBounds'
        isEqualToBounds.geometry = Polygon(
            ((0, 0), (0, 85.05113), (180, 85.05113), (180, 0), (0, 0))
        )
        isEqualToBounds.save()

        # Rectangle with bottom left at (-1,1), top right at (5,5)
        overlaps = Location()
        overlaps.name = 'overlaps'
        overlaps.geometry = Polygon(((-1, 1), (5, 1), (5, 5), (-1, 5), (-1, 1)))
        overlaps.save()

        # Rectangle with bottom left at (-3,-3), top right at (-1,2)
        nonIntersecting = Location()
        nonIntersecting.name = 'nonIntersecting'
        nonIntersecting.geometry = Polygon(
            ((-3, -3), (-1, -3), (-1, 2), (-3, 2), (-3, -3))
        )
        nonIntersecting.save()

        # Make sure we only get back the ones strictly contained in the bounding box
        response = self.client.get(
            self.location_contained_in_tile_list_url + url_params
        )
        self.assertEqual(len(response.data['features']), 2)
        for result in response.data['features']:
            self.assertEqual(
                result['properties']['name'] in ('isContained', 'isEqualToBounds'), True
            )

        # Make sure we get overlapping results for the view which allows bounding box overlaps.
        response = self.client.get(self.location_overlaps_tile_list_url + url_params)
        self.assertEqual(len(response.data['features']), 3)
        for result in response.data['features']:
            self.assertEqual(
                result['properties']['name']
                in ('isContained', 'isEqualToBounds', 'overlaps'),
                True,
            )

    @skipIf(
        has_spatialite, 'Skipped test for spatialite backend: missing feature "dwithin"'
    )
    def test_DistanceToPointFilter_filtering(self):
        """
        Checks that the DistanceFilter returns only objects within the given distance of the
        given geometry defined by the URL parameters
        """
        self.assertEqual(Location.objects.count(), 0)

        # Filter parameters
        distance = 5000  # meters
        point_on_alcatraz = [-122.4222, 37.82667]

        url_params = '?dist=%0.4f&point=hello&format=json' % (distance,)
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertEqual(response.status_code, 400)

        url_params = '?dist=%0.4f&point=%0.4f,%0.4f&format=json' % (
            distance,
            point_on_alcatraz[0],
            point_on_alcatraz[1],
        )

        treasure_island = Location()
        treasure_island.name = "Treasure Island"
        treasure_island.geometry = self.treasure_island_geom
        treasure_island.full_clean()
        treasure_island.save()

        ggpark = Location()
        ggpark.name = "Golden Gate Park"
        ggpark.geometry = self.ggpark_geom
        ggpark.save()

        # Make sure we only get back the ones within the distance
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertEqual(len(response.data['features']), 1)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'], treasure_island.name)

        # Make sure we get back all the ones within the distance
        distance = 7000
        url_params = '?dist=%0.4f&point=%0.4f,%0.4f&format=json' % (
            distance,
            point_on_alcatraz[0],
            point_on_alcatraz[1],
        )
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertEqual(len(response.data['features']), 2)
        for result in response.data['features']:
            self.assertIn(
                result['properties']['name'], (ggpark.name, treasure_island.name)
            )

        # Make sure we only get back the ones within the distance
        degrees = 0.05
        url_params = '?dist=%0.4f&point=%0.4f,%0.4f&format=json' % (
            degrees,
            point_on_alcatraz[0],
            point_on_alcatraz[1],
        )
        response = self.client.get(
            self.location_within_degrees_of_point_list_url + url_params
        )
        self.assertEqual(len(response.data['features']), 1)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'], treasure_island.name)

    @skipIf(
        has_spatialite,
        'Skipped test for spatialite backend: missing feature "GeometryDistance"',
    )
    @skipIf(
        not has_geometry_distance,
        'Skipped test for Django < 3.0: missing feature "GeometryDistance"',
    )
    def test_DistanceToPointOrderingFilter_filtering(self):
        """
        Checks that the DistanceOrderingFilter returns the objects in the correct order
        given the geometry defined by the URL parameters
        """
        self.assertEqual(Location.objects.count(), 0)

        url_params = '?point=hello&format=json'
        response = self.client.get(
            '%s%s' % (self.location_order_distance_to_point, url_params)
        )
        self.assertEqual(response.status_code, 400)

        Location.objects.create(
            name='Houston', geometry='SRID=4326;POINT (-95.363151 29.763374)'
        )
        Location.objects.create(
            name='Dallas', geometry='SRID=4326;POINT (-96.801611 32.782057)'
        )
        Location.objects.create(
            name='Oklahoma City', geometry='SRID=4326;POINT (-97.521157 34.464642)'
        )
        Location.objects.create(
            name='Wellington', geometry='SRID=4326;POINT (174.783117 -41.315268)'
        )
        Location.objects.create(
            name='Pueblo', geometry='SRID=4326;POINT (-104.609252 38.255001)'
        )
        Location.objects.create(
            name='Lawrence', geometry='SRID=4326;POINT (-95.235060 38.971823)'
        )
        Location.objects.create(
            name='Chicago', geometry='SRID=4326;POINT (-87.650175 41.850385)'
        )
        Location.objects.create(
            name='Victoria', geometry='SRID=4326;POINT (-123.305196 48.462611)'
        )

        point = [-90, 40]

        url_params = '?point=%i,%i&format=json' % (point[0], point[1])
        response = self.client.get(
            '%s%s' % (self.location_order_distance_to_point, url_params)
        )
        self.assertEqual(len(response.data['features']), 8)
        self.assertEqual(
            [city['properties']['name'] for city in response.data['features']],
            [
                'Chicago',
                'Lawrence',
                'Oklahoma City',
                'Dallas',
                'Houston',
                'Pueblo',
                'Victoria',
                'Wellington',
            ],
        )

        url_params = '?point=%i,%i&order=desc&format=json' % (point[0], point[1])
        response = self.client.get(
            '%s%s' % (self.location_order_distance_to_point, url_params)
        )
        self.assertEqual(len(response.data['features']), 8)
        self.assertEqual(
            [city['properties']['name'] for city in response.data['features']],
            [
                'Wellington',
                'Victoria',
                'Pueblo',
                'Houston',
                'Dallas',
                'Oklahoma City',
                'Lawrence',
                'Chicago',
            ],
        )

    @skipIf(
        has_spatialite,
        'Skipped test for spatialite backend: missing feature "contains_properly"',
    )
    def test_GeometryField_filtering(self):
        """Checks that the GeometryField allows sane filtering."""
        self.assertEqual(Location.objects.count(), 0)

        treasure_island = Location()
        treasure_island.name = "Treasure Island"
        treasure_island.geometry = self.treasure_island_geom
        treasure_island.full_clean()
        treasure_island.save()

        ggpark = Location()
        ggpark.name = "Golden Gate Park"
        ggpark.geometry = self.ggpark_geom
        ggpark.save()

        point_inside_ggpark_geojson = """
        { "type": "Point", "coordinates": [ -122.49034881591797, 37.76949349270407 ] }
        """

        try:
            quoted_param = urllib.quote(point_inside_ggpark_geojson)
        except AttributeError:
            quoted_param = urllib.parse.quote(point_inside_ggpark_geojson)

        url_params = "?contains_properly=%s" % (quoted_param,)

        response = self.client.get(
            '{0}{1}'.format(self.geojson_contained_in_geometry, url_params)
        )
        self.assertEqual(len(response.data), 1)

        geometry_response = GEOSGeometry(json.dumps(response.data[0]['geometry']))

        self.assertTrue(geometry_response.equals_exact(self.ggpark_geom))
        self.assertEqual(response.data[0]['name'], ggpark.name)

        # try without any param, should return both
        response = self.client.get(self.geojson_contained_in_geometry)
        self.assertEqual(len(response.data), 2)

    def test_inBBOXFilter_filtering_none(self):
        url_params = '?in_bbox=&format=json'
        response = self.client.get(
            self.location_contained_in_bbox_list_url + url_params
        )
        self.assertDictEqual(
            response.data, {'type': 'FeatureCollection', 'features': []}
        )

    def test_inBBOXFilter_ValueError(self):
        url_params = '?in_bbox=0&format=json'
        response = self.client.get(
            self.location_contained_in_bbox_list_url + url_params
        )
        self.assertEqual(
            response.data['detail'],
            'Invalid bbox string supplied for parameter in_bbox',
        )

    def test_inBBOXFilter_filter_field_none(self):
        original_value = GeojsonLocationContainedInBBoxList.bbox_filter_field
        GeojsonLocationContainedInBBoxList.bbox_filter_field = None
        url_params = '?in_bbox=0,0,0,0&format=json'
        response = self.client.get(
            self.location_contained_in_bbox_list_url + url_params
        )
        self.assertDictEqual(
            response.data, {'type': 'FeatureCollection', 'features': []}
        )
        GeojsonLocationContainedInBBoxList.bbox_filter_field = original_value

    def test_TileFilter_filtering_none(self):
        url_params = '?tile=&format=json'
        response = self.client.get(
            self.location_contained_in_tile_list_url + url_params
        )
        self.assertEqual(response.data, {'type': 'FeatureCollection', 'features': []})

    def test_TileFilter_ValueError(self):
        url_params = '?tile=1/0&format=json'
        response = self.client.get(
            self.location_contained_in_tile_list_url + url_params
        )
        self.assertEqual(
            response.data['detail'], 'Invalid tile string supplied for parameter tile'
        )

    def test_DistanceToPointFilter_filtering_none(self):
        url_params = '?dist=5000&point=&format=json'
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertDictEqual(
            response.data, {'type': 'FeatureCollection', 'features': []}
        )

    def test_DistanceToPointFilter_filter_field_none(self):
        original_value = GeojsonLocationWithinDistanceOfPointList.distance_filter_field
        GeojsonLocationWithinDistanceOfPointList.distance_filter_field = None
        url_params = '?dist=5000&point=&format=json'
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertDictEqual(
            response.data, {'type': 'FeatureCollection', 'features': []}
        )
        GeojsonLocationWithinDistanceOfPointList.distance_filter_field = original_value

    def test_DistanceToPointFilter_ValueError_point(self):
        url_params = '?dist=500.0&point=hello&format=json'
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertEqual(
            response.data['detail'],
            'Invalid geometry string supplied for parameter point',
        )

    def test_DistanceToPointFilter_ValueError_distance(self):
        url_params = '?dist=wrong&point=12.0,42.0&format=json'
        response = self.client.get(
            '%s%s' % (self.location_within_distance_of_point_list_url, url_params)
        )
        self.assertEqual(
            response.data['detail'],
            'Invalid distance string supplied for parameter dist',
        )

    @skipIf(
        not has_geometry_distance,
        'Skipped test for Django < 3.0: missing feature "GeometryDistance"',
    )
    def test_DistanceToPointOrderingFilter_filtering_none(self):
        url_params = '?point=&format=json'
        response = self.client.get(
            '%s%s' % (self.location_order_distance_to_point, url_params)
        )
        self.assertDictEqual(
            response.data, {'type': 'FeatureCollection', 'features': []}
        )

    @skipIf(
        not has_geometry_distance,
        'Skipped test for Django < 3.0: missing feature "GeometryDistance"',
    )
    def test_DistanceToPointOrderingFilter_ordering_filter_field_none(self):
        original_value = (
            GeojsonLocationOrderDistanceToPointList.distance_ordering_filter_field
        )
        GeojsonLocationOrderDistanceToPointList.distance_ordering_filter_field = None
        url_params = '?point=&format=json'
        response = self.client.get(
            '%s%s' % (self.location_order_distance_to_point, url_params)
        )
        self.assertDictEqual(
            response.data, {'type': 'FeatureCollection', 'features': []}
        )
        GeojsonLocationOrderDistanceToPointList.distance_ordering_filter_field = (
            original_value
        )

    @skipIf(has_geometry_distance, 'Skipped test for Django >= 3.0')
    def test_DistanceToPointOrderingFilter_not_available(self):
        url_params = '?point=12,42&format=json'
        with self.assertRaises(ValueError):
            self.client.get(
                '%s%s' % (self.location_order_distance_to_point, url_params)
            )
