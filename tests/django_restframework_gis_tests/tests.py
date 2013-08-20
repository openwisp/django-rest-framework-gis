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
        
    def test_get_location_list(self):
        response = self.client.get(self.location_list_url)
        self.assertEqual(response.status_code, 200)
    
    def test_post_location_list(self):
        self.assertEqual(Location.objects.count(), 0)
        
        data = {
            'name': 'geojson input test',
            'geometry': {
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
