"""
unit tests for restframework_gis
"""

try:
    import simplejson as json
except ImportError:
    import json


import urllib
import sys
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry, Polygon, Point
from django.core.urlresolvers import reverse

from .models import Location


class TestRestFrameworkGis(TestCase):

    def setUp(self):
        self.location_list_url = reverse('api_location_list')
        self.geojson_location_list_url = reverse('api_geojson_location_list')
        self.geos_error_message = 'Invalid format: string or unicode input unrecognized as WKT EWKT, and HEXEWKB.'

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
        self.assertEqual(response.data['geometry'][0], u'This field is required.')

        data = { 'name': 'empty input test', 'geometry': '' }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], u'This field is required.')

        data = { 'name': 'empty input test' }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], u'This field is required.')

        data = { 'name': 'empty input test', 'geometry': '' }
        response = self.client.post(self.location_list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data['geometry'][0], u'This field is required.')

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
        location = Location.objects.create(name='geojson test', geometry='POINT (135.0 45.0)')

        url = reverse('api_geojson_location_details', args=[location.id])
        expected = {
            'id': location.id,
            'type': 'Feature',
            'properties': {
                'details': "http://testserver/geojson/%s/" % location.id,
                'name': 'geojson test',
                'fancy_name': 'Kool geojson test',
                'slug': 'geojson-test',
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    135.0,
                    45.0,
                ],
            }
        }
        response = self.client.get(url)
        if sys.version_info>(3,0,0):
            self.assertCountEqual(json.dumps(response.data), json.dumps(expected))
        else:
            self.assertItemsEqual(json.dumps(response.data), json.dumps(expected))

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
        self.assertContains(response, '<textarea name="geometry"')
        self.assertContains(response, '&quot;type&quot;: &quot;Point&quot;')
        self.assertContains(response, '&quot;coordinates&quot;: [')
        # textarea input should contain valid GeoJSON indented for readability
        # doesn't seem possible with DRF 3.0
        # let's wait for DRF 3.1
        #self.assertNotContains(response, 'u&#39;type&#39;: u&#39;Point&#39;, u&#39;coordinates&#39;:')

    def test_patch_geojson_location(self):
        location = Location.objects.create(name='geojson patch test', geometry='POINT (135.0 45.0)')

        url = reverse('api_geojson_location_details', args=[location.id])
        data = {
            "properties": {
                "name":"geojson successful patch test"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [10.1, 10.1]
            } 
        }
        response = self.client.generic('PATCH', url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        location_reloaded = Location.objects.get(pk=location.id)
        self.assertEquals(location_reloaded.name, 'geojson successful patch test')
        self.assertEquals(location_reloaded.geometry, Point(10.1, 10.1))

    def test_patch_geojson_location_wo_changing_geometry(self):
        location = Location.objects.create(name='geojson patch test', geometry='POINT (135.0 45.0)')

        url = reverse('api_geojson_location_details', args=[location.id])
        data = {
            "properties": {
                "name":"geojson successful patch test"
            }
        }
        response = self.client.generic('PATCH', url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        location_reloaded = Location.objects.get(pk=location.id)
        self.assertEquals(location_reloaded.name, 'geojson successful patch test')
        self.assertEquals(location_reloaded.geometry, Point(135.0, 45.0))
