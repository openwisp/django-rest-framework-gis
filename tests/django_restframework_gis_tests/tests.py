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
        self.location_list_url = reverse('api_location_list')
        self.geojson_location_list_url = reverse('api_geojson_location_list')
        self.location_contained_in_bbox_list_url = reverse('api_geojson_location_list_contained_in_bbox_filter')
        self.location_overlaps_bbox_list_url = reverse('api_geojson_location_list_overlaps_bbox_filter')
        self.geos_error_message = 'Invalid format: string or unicode input unrecognized as WKT EWKT, and HEXEWKB.'
        self.geojson_contained_in_geometry = reverse('api_geojson_contained_in_geometry')
    
    def _create_locations(self):
        self.l1 = Location.objects.create(id=1, name='l1', slug='l1', geometry='POINT (13.0078125000020002 42.4234565179379999)')
        self.l2 = Location.objects.create(id=2, name='l2', slug='l2', geometry='POINT (12.0078125000020002 43.4234565179379999)')
    
    def test_get_location_list(self):
        response = self.client.get(self.location_list_url)
        self.assertEqual(response.status_code, 200)
    
    def test_post_location_list_geojson(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "geojson input test",
            "geometry": {
                "type": "GeometryCollection", 
                "geometries": [
                    {
                        "type": "Point", 
                        "coordinates": [
                            12.492324113849, 
                            41.890307434153
                        ]
                    }
                ]
            }
        }
        
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        data = {
            "name": "geojson input test2",
            "geometry": {
                "type": "Point", 
                "coordinates": [
                    12.492324113849, 
                    41.890307434153
                ]
            }
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 2)
    
    def test_post_location_list_geojson_as_multipartformdata(self):
        """ emulate sending geojson string in webform """
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "geojson input test",
            "geometry": json.dumps({
                "type": "GeometryCollection", 
                "geometries": [
                    {
                        "type": "Point", 
                        "coordinates": [
                            12.492324113849, 
                            41.890307434153
                        ]
                    }
                ]
            })
        }
        
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
    
    def test_post_HTML_browsable_api(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "geojson input test2",
            "slug": "prova",
            "geometry": json.dumps({
                "type": "GeometryCollection", 
                "geometries": [
                    {
                        "type": "Point", 
                        "coordinates": [
                            12.492324113849, 
                            41.890307434153
                        ]
                    }
                ]
            })
        }
        response = self.client.post(self.location_list_url, data, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        location = Location.objects.all()[0]
        self.assertEqual(location.name, 'geojson input test2')
        self.assertEqual(location.slug, 'prova')
    
    def test_post_location_list_WKT(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            'name': 'WKT input test',
            'geometry': 'POINT (12.492324113849 41.890307434153)'
        }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
    
    def test_post_location_list_WKT_as_json(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            'name': 'WKT input test',
            'geometry': 'POINT (12.492324113849 41.890307434153)'
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
    
    def test_post_location_list_empty_geometry(self):
        data = { 'name': 'empty input test' }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
        
        data = { 'name': 'empty input test', 'geometry': '' }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
        
        data = { 'name': 'empty input test' }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
        
        data = { 'name': 'empty input test', 'geometry': '' }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
    
    def test_post_location_list_invalid_WKT(self):
        data = {
            'name': 'WKT wrong input test',
            'geometry': 'I AM OBVIOUSLY WRONG'
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        
        # repeat as multipart form data
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        
        data = {
            'name': 'I AM MODERATELY WRONG',
            'geometry': 'POINT (12.492324113849, 41.890307434153)'
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        
        # repeat as multipart form data
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
    
    def test_post_location_list_invalid_geojson(self):
        data = {
            "name": "quite wrong",
            "geometry": {
                "type": "ARRRR", 
                "dasdas": [
                    {
                        "STtype": "PTUAMAoint", 
                        "NNAare":"rgon"
                    }
                ]
            }
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        
        data = {
            "name": "very wrong",
            "geometry": ['a', 'b', 'c']
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        
        data = {
            "name": "very wrong",
            "geometry": False
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        
        data = {
            "name": "very wrong",
            "geometry": { "value": { "nested": ["yo"] } }
        }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
    
    def test_geojson_format(self):
        """ test geojson format """
        location = Location.objects.create(name='geojson test', geometry='POINT (10.1 10.1)')
        
        url = reverse('api_geojson_location_details', args=[location.id])
        response = self.client.get(url)
        self.assertEqual(response.data['type'], "Feature")
        self.assertEqual(response.data['properties']['name'], "geojson test")
        self.assertEqual(response.data['properties']['fancy_name'], "Kool geojson test")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]")
        
        response = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertContains(response, "Kool geojson test")
    
    def test_geojson_id_attribute(self):
        location = Location.objects.create(name='geojson test', geometry='POINT (10.1 10.1)')
        
        url = reverse('api_geojson_location_details', args=[location.id])
        response = self.client.get(url)
        self.assertEqual(response.data['id'], location.id)
    
    def test_geojson_id_attribute_slug(self):
        location = Location.objects.create(name='geojson test', geometry='POINT (10.1 10.1)')
        
        url = reverse('api_geojson_location_slug_details', args=[location.slug])
        response = self.client.get(url)
        self.assertEqual(response.data['id'], location.slug)
    
    def test_geojson_false_id_attribute_slug(self):
        location = Location.objects.create(name='geojson test', geometry='POINT (10.1 10.1)')
        
        url = reverse('api_geojson_location_falseid_details', args=[location.id])
        response = self.client.get(url)
        with self.assertRaises(KeyError):
            response.data['id']
    
    def test_post_geojson_location_list(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "type": "Feature", 
            "properties": {
                "name": "point?",
                "details": "ignore this"
            }, 
            "geometry": {
                "type": "Point", 
                "coordinates": [
                    10.1, 
                    10.1
                ]
            }
        }
        
        response = self.client.post(self.geojson_location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        url = reverse('api_geojson_location_details', args=[Location.objects.order_by('-id')[0].id])
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], "point?")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]")
        self.assertNotEqual(response.data['properties']['details'], "ignore this")
    
    def test_post_geojson_location_list_HTML(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "type": "Feature", 
            "properties": {
                "name": "point?",
                "details": "ignore this"
            }, 
            "geometry": {
                "type": "Point", 
                "coordinates": [
                    10.1, 
                    10.1
                ]
            }
        }
        
        response = self.client.post(self.geojson_location_list_url, data=json.dumps(data), content_type='application/json', HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        url = reverse('api_geojson_location_details', args=[Location.objects.order_by('-id')[0].id])
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], "point?")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]")
        self.assertNotEqual(response.data['properties']['details'], "ignore this")
    
    def test_post_invalid_geojson_location_list(self):
        data = {
            "type": "Feature", 
            "properties": {
                "details": "ignore this"
            }, 
            "geometry": {
                "type": "Point", 
                "coordinates": [
                    10.1, 
                    10.1
                ]
            }
        }
        
        response = self.client.post(self.geojson_location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(response.data['name'][0], "This field is required.")
        
        data = {
            "type": "Feature", 
            "properties": {
                "name": "point?",
            }, 
            "geometry": {
                "type": "Point", 
                "WRONG": {}
            }
        }
        response = self.client.post(self.geojson_location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
    
    def test_post_geojson_location_list_WKT(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "type": "Feature", 
            "properties": {
                "name": "point?",
            }, 
            "geometry": "POINT (10.1 10.1)"
        }
        
        response = self.client.post(self.geojson_location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        url = reverse('api_geojson_location_details', args=[Location.objects.order_by('-id')[0].id])
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], "point?")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]")
    
    def test_geofeatured_model_serializer_compatible_with_geomodel_serializer(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "geojson input test",
            "geometry": {
                "type": "GeometryCollection", 
                "geometries": [
                    {
                        "type": "Point", 
                        "coordinates": [
                            12.492324113849, 
                            41.890307434153
                        ]
                    }
                ]
            }
        }
        
        response = self.client.post(self.geojson_location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
    
    def test_geofeatured_model_post_as_multipartformdata(self):
        """ emulate sending geojson string in webform """
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "geojson input test",
            "geometry": json.dumps({
                "type": "Point", 
                "coordinates": [
                    12.492324113849, 
                    41.890307434153
                ]
            })
        }
        
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(response.data['geometry']['type'], "Point")
        
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
    
    def test_HTML_browsable_geojson_location_list(self):
        response = self.client.get(self.geojson_location_list_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        
        self._create_locations()
        
        response = self.client.get(self.geojson_location_list_url, HTTP_ACCEPT='text/html')
        self.assertContains(response, 'l1')
        self.assertContains(response, 'l2')
    
    def test_post_geojson_location_list_HTML_web_form(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "HTML test",
            "geometry": json.dumps({
                "type": "Point", 
                "coordinates": [
                    10.1, 
                    10.1
                ]
            })
        }
        
        response = self.client.post(self.geojson_location_list_url, data, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        location = Location.objects.all()[0]
        self.assertEqual(location.name, "HTML test")
        self.assertEqual(location.geometry.geom_type, "Point")
    
    def test_post_geojson_location_list_HTML_web_form_WKT(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            "name": "HTML test WKT",
            "geometry": "POINT (10.1 10.1)"
        }
        
        response = self.client.post(self.geojson_location_list_url, data, HTTP_ACCEPT='text/html')
        #print response.content
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        
        location = Location.objects.all()[0]
        self.assertEqual(location.name, "HTML test WKT")
    
    def test_geojson_HTML_widget_value(self):
        self._create_locations()
        response = self.client.get(self.geojson_location_list_url, HTTP_ACCEPT='text/html')
        self.assertContains(response, '<textarea cols="40" id="geometry"')
        self.assertContains(response, '&quot;type&quot;: &quot;Point&quot;')
        self.assertContains(response, '&quot;coordinates&quot;: [')
