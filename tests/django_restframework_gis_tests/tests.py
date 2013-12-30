"""
unit tests for restframework_gis
"""

try:
    import simplejson as json
except ImportError:
    import json


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
        """ Checks that the inBBOXFilter returns only objects strictly contained in
            the bounding box given by the in_bbox URL parameter """
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