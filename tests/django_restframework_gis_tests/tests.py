"""
unit tests for restframework_gis
"""

try:
    import simplejson as json
except Exception:
    import json


from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from django.core.urlresolvers import reverse

from .models import Location


class TestRestFrameworkGis(TestCase):
    
    def setUp(self):
        self.location_list_url = reverse('api_location_list')
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
    