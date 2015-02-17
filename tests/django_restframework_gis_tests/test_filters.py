"""
unit tests for restframework_gis
"""

try:
    import simplejson as json
except ImportError:
    import json


import urllib
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.urlresolvers import reverse

from .models import Location


class TestRestFrameworkGis(TestCase):

    def setUp(self):
        self.location_contained_in_bbox_list_url = reverse('api_geojson_location_list_contained_in_bbox_filter')
        self.location_overlaps_bbox_list_url = reverse('api_geojson_location_list_overlaps_bbox_filter')
        self.location_contained_in_tile_list_url = reverse('api_geojson_location_list_contained_in_tile_filter')
        self.location_overlaps_tile_list_url = reverse('api_geojson_location_list_overlaps_tile_filter')
        self.location_within_distance_of_point_list_url = reverse('api_geojson_location_list_within_distance_of_point_filter')
        self.location_within_degrees_of_point_list_url = reverse('api_geojson_location_list_within_degrees_of_point_filter')
        self.geojson_contained_in_geometry = reverse('api_geojson_contained_in_geometry')

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
        isContained.geometry = Polygon(((1,1),(9,1),(9,9),(1,9),(1,1)))
        isContained.save()

        isEqualToBounds = Location()
        isEqualToBounds.name = 'isEqualToBounds'
        isEqualToBounds.geometry = Polygon(((0,0),(10,0),(10,10),(0,10),(0,0)))
        isEqualToBounds.save()

        # Rectangle with bottom left at (-1,1), top right at (5,5)
        overlaps = Location()
        overlaps.name = 'overlaps'
        overlaps.geometry = Polygon(((-1,1),(5,1),(5,5),(-1,5),(-1,1)))
        overlaps.save()

        # Rectangle with bottom left at (-3,-3), top right at (-1,2)
        nonIntersecting = Location()
        nonIntersecting.name = 'nonIntersecting'
        nonIntersecting.geometry = Polygon(((-3,-3),(-1,-3),(-1,2),(-3,2),(-3,-3)))
        nonIntersecting.save()

        # Make sure we only get back the ones strictly contained in the bounding box
        response = self.client.get(self.location_contained_in_bbox_list_url + url_params)
        self.assertEqual(len(response.data['features']), 2)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in ('isContained', 'isEqualToBounds'), True)

        # Make sure we get overlapping results for the view which allows bounding box overlaps.
        response = self.client.get(self.location_overlaps_bbox_list_url + url_params)
        self.assertEqual(len(response.data['features']), 3)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in ('isContained', 'isEqualToBounds', 'overlaps'), True)

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
        isContained.geometry = Polygon(((1,1),(9,1),(9,9),(1,9),(1,1)))
        isContained.save()

        isEqualToBounds = Location()
        isEqualToBounds.name = 'isEqualToBounds'
        isEqualToBounds.geometry = Polygon(((0,0),(0,85.05113),(180,85.05113),(180,0),(0,0)))
        isEqualToBounds.save()

        # Rectangle with bottom left at (-1,1), top right at (5,5)
        overlaps = Location()
        overlaps.name = 'overlaps'
        overlaps.geometry = Polygon(((-1,1),(5,1),(5,5),(-1,5),(-1,1)))
        overlaps.save()

        # Rectangle with bottom left at (-3,-3), top right at (-1,2)
        nonIntersecting = Location()
        nonIntersecting.name = 'nonIntersecting'
        nonIntersecting.geometry = Polygon(((-3,-3),(-1,-3),(-1,2),(-3,2),(-3,-3)))
        nonIntersecting.save()

        # Make sure we only get back the ones strictly contained in the bounding box
        response = self.client.get(self.location_contained_in_tile_list_url + url_params)
        self.assertEqual(len(response.data['features']), 2)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in ('isContained', 'isEqualToBounds'), True)

        # Make sure we get overlapping results for the view which allows bounding box overlaps.
        response = self.client.get(self.location_overlaps_tile_list_url + url_params)
        self.assertEqual(len(response.data['features']), 3)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in ('isContained', 'isEqualToBounds', 'overlaps'), True)

    def test_DistanceToPointFilter_filtering(self):
        """
        Checks that the DistancFilter returns only objects within the given distance of the
        given geometry defined by the URL parameters
        """
        self.assertEqual(Location.objects.count(), 0)

        # Filter parameters
        distance = 5000 #meters
        point_inside_ggpark = [-122.49034881591797, 37.76949349270407]
        point_on_golden_gate_bridge = [-122.47894, 37.8199]
        point_on_alcatraz = [-122.4222, 37.82667]
        point_on_treasure_island = [-122.3692, 37.8244]
        point_on_angel_island = [-122.4326, 37.86091]

        url_params = '?dist=%0.4f&point=%0.4f,%0.4f&format=json' % (distance, point_on_alcatraz[0], point_on_alcatraz[1])

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

        treasure_island_geom = GEOSGeometry(treasure_island_geojson)
        treasure_island = Location()
        treasure_island.name = "Treasure Island"
        treasure_island.geometry = treasure_island_geom
        treasure_island.full_clean()
        treasure_island.save()

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
        ggpark_geom = GEOSGeometry(ggpark_geojson)
        ggpark = Location()
        ggpark.name = "Golden Gate Park"
        ggpark.geometry = ggpark_geom
        ggpark.save()

        # Make sure we only get back the ones within the distance
        response = self.client.get('%s%s' % (self.location_within_distance_of_point_list_url, url_params))
        self.assertEqual(len(response.data['features']), 1)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in (treasure_island.name), True)

        # Make sure we get back all the ones within the distance
        distance = 7000
        url_params = '?dist=%0.4f&point=%0.4f,%0.4f&format=json' % (distance, point_on_alcatraz[0], point_on_alcatraz[1])
        response = self.client.get('%s%s' % (self.location_within_distance_of_point_list_url, url_params))
        self.assertEqual(len(response.data['features']), 2)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in (ggpark.name, treasure_island.name), True)

        # Make sure we only get back the ones within the distance
        degrees = .05
        url_params = '?dist=%0.4f&point=%0.4f,%0.4f&format=json' % (degrees, point_on_alcatraz[0], point_on_alcatraz[1])
        response = self.client.get(self.location_within_degrees_of_point_list_url + url_params)
        self.assertEqual(len(response.data['features']), 1)
        for result in response.data['features']:
            self.assertEqual(result['properties']['name'] in (treasure_island.name), True)

    def test_GeometryField_filtering(self):
        """ Checks that the GeometryField allows sane filtering. """
        self.assertEqual(Location.objects.count(), 0)

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

        treasure_island_geom = GEOSGeometry(treasure_island_geojson)
        treasure_island = Location()
        treasure_island.name = "Treasure Island"
        treasure_island.geometry = treasure_island_geom
        treasure_island.full_clean()
        treasure_island.save()

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
        ggpark_geom = GEOSGeometry(ggpark_geojson)
        ggpark = Location()
        ggpark.name = "Golden Gate Park"
        ggpark.geometry = ggpark_geom
        ggpark.save()

        point_inside_ggpark_geojson = """{ "type": "Point", "coordinates": [ -122.49034881591797, 37.76949349270407 ] }"""

        try:
            quoted_param = urllib.quote(point_inside_ggpark_geojson)
        except AttributeError:
            quoted_param = urllib.parse.quote(point_inside_ggpark_geojson)

        url_params = "?contains_properly=%s" % quoted_param

        response = self.client.get(self.geojson_contained_in_geometry + url_params)
        self.assertEqual(len(response.data), 1)

        geometry_response = GEOSGeometry(json.dumps(response.data[0]['geometry']))

        self.assertTrue(geometry_response.equals_exact(ggpark_geom))
        self.assertEqual(response.data[0]['name'], ggpark.name)

        # try without any param, should return both
        response = self.client.get(self.geojson_contained_in_geometry)
        self.assertEqual(len(response.data), 2)
