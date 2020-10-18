"""
unit tests for restframework_gis
"""

import json
import pickle
import sys
from unittest import skipIf

import django
from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import TestCase

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

import rest_framework
from django.core.exceptions import ImproperlyConfigured

from rest_framework_gis import serializers as gis_serializers
from rest_framework_gis.fields import GeoJsonDict

from .models import LocatedFile, Location, Nullable
from .serializers import LocationGeoSerializer

is_pre_drf_39 = not rest_framework.VERSION.startswith('3.9')


class TestRestFrameworkGis(TestCase):
    def setUp(self):
        self.location_list_url = reverse('api_location_list')
        self.geojson_location_list_url = reverse('api_geojson_location_list')
        self.geos_error_message = (
            'Invalid format: string or unicode input unrecognized as GeoJSON,'
            ' WKT EWKT or HEXEWKB.'
        )
        self.gdal_error_message = (
            'Unable to convert to python object:'
            ' Invalid geometry pointer returned from "OGR_G_CreateGeometryFromJson".'
        )
        if django.VERSION >= (2, 0, 0):
            self.value_error_message = (
                "Unable to convert to python object:"
                " String input unrecognized as WKT EWKT, and HEXEWKB."
            )
        else:
            self.value_error_message = (
                "Unable to convert to python object:"
                " String or unicode input unrecognized as WKT EWKT, and HEXEWKB."
            )
        self.type_error_message = (
            "Unable to convert to python object: Improper geometry input type:"
        )

    def _create_locations(self):
        self.l1 = Location.objects.create(
            id=1,
            name='l1',
            slug='l1',
            geometry='POINT (13.0078125000020002 42.4234565179379999)',
        )
        self.l2 = Location.objects.create(
            id=2,
            name='l2',
            slug='l2',
            geometry='POINT (12.0078125000020002 43.4234565179379999)',
        )

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
                    {"type": "Point", "coordinates": [12.492324113849, 41.890307434153]}
                ],
            },
        }
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        data = {
            "name": "geojson input test2",
            "geometry": {
                "type": "Point",
                "coordinates": [12.492324113849, 41.890307434153],
            },
        }
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 2)

    def test_post_location_list_geojson_as_multipartformdata(self):
        """ emulate sending geojson string in webform """
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "name": "geojson input test",
            "geometry": json.dumps(
                {
                    "type": "GeometryCollection",
                    "geometries": [
                        {
                            "type": "Point",
                            "coordinates": [12.492324113849, 41.890307434153],
                        }
                    ],
                }
            ),
        }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)

    def test_post_HTML_browsable_api(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "name": "geojson input test2",
            "slug": "prova",
            "geometry": json.dumps(
                {
                    "type": "GeometryCollection",
                    "geometries": [
                        {
                            "type": "Point",
                            "coordinates": [12.492324113849, 41.890307434153],
                        }
                    ],
                }
            ),
        }
        response = self.client.post(
            self.location_list_url, data, HTTP_ACCEPT='text/html'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        location = Location.objects.all()[0]
        self.assertEqual(location.name, 'geojson input test2')
        self.assertEqual(location.slug, 'prova')

    def test_post_location_list_WKT(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            'name': 'WKT input test',
            'geometry': 'POINT (12.492324113849 41.890307434153)',
        }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)

    def test_post_location_list_EWKT(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            'name': 'EWKT input test',
            'geometry': 'SRID=28992;POINT(221160 600204)',
        }
        response = self.client.post(self.location_list_url, data)
        expected_coords = (6.381495826183805, 53.384066927384985)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        for lat, lon in zip(
            Location.objects.get(name='EWKT input test').geometry.coords,
            expected_coords,
        ):
            self.assertAlmostEqual(lat, lon, places=5)

    def test_post_location_list_WKT_as_json(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            'name': 'WKT input test',
            'geometry': 'POINT (12.492324113849 41.890307434153)',
        }
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)

    def test_post_location_list_empty_geometry(self):
        data = {'name': 'empty input test'}
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
        data = {'name': 'empty input test', 'geometry': ''}
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
        data = {'name': 'empty input test'}
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0], 'This field is required.')
        data = {'name': 'empty input test', 'geometry': ''}
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0], 'This field is required.')

    def test_post_location_list_invalid_WKT(self):
        data = {'name': 'WKT wrong input test', 'geometry': 'I AM OBVIOUSLY WRONG'}
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(response.data['geometry'][0], self.value_error_message)
        # repeat as multipart form data
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], self.value_error_message)
        data = {
            'name': 'I AM MODERATELY WRONG',
            'geometry': 'POINT (12.492324113849, 41.890307434153)',
        }
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)
        # repeat as multipart form data
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.data['geometry'][0], self.geos_error_message)

    def test_post_location_list_invalid_geojson(self):
        data = {
            "name": "quite wrong",
            "geometry": {
                "type": "ARRRR",
                "dasdas": [{"STtype": "PTUAMAoint", "NNAare": "rgon"}],
            },
        }
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0], self.gdal_error_message)
        data = {"name": "very wrong", "geometry": ['a', 'b', 'c']}
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0][0:65], self.type_error_message)
        data = {"name": "very wrong", "geometry": False}
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0][0:65], self.type_error_message)
        data = {"name": "very wrong", "geometry": {"value": {"nested": ["yo"]}}}
        response = self.client.post(
            self.location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.data['geometry'][0], self.gdal_error_message)

    def test_geojson_format(self):
        """ test geojson format """
        location = Location.objects.create(
            name='geojson test', geometry='POINT (135.0 45.0)'
        )
        url = reverse('api_geojson_location_details', args=[location.id])
        expected = {
            'id': location.id,
            'type': 'Feature',
            'properties': {
                'details': "http://testserver/geojson/%s/" % location.id,
                'name': 'geojson test',
                'fancy_name': 'Kool geojson test',
                'timestamp': None,
                'slug': 'geojson-test',
            },
            'geometry': {'type': 'Point', 'coordinates': [135.0, 45.0]},
        }
        response = self.client.get(url)
        if sys.version_info > (3, 0, 0):
            self.assertCountEqual(json.dumps(response.data), json.dumps(expected))
        else:
            self.assertItemsEqual(json.dumps(response.data), json.dumps(expected))
        response = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertContains(response, "Kool geojson test")

    def test_geojson_id_attribute(self):
        location = Location.objects.create(
            name='geojson test', geometry='POINT (10.1 10.1)'
        )
        url = reverse('api_geojson_location_details', args=[location.id])
        response = self.client.get(url)
        self.assertEqual(response.data['id'], location.id)

    def test_geojson_id_attribute_slug(self):
        location = Location.objects.create(
            name='geojson test', geometry='POINT (10.1 10.1)'
        )
        url = reverse('api_geojson_location_slug_details', args=[location.slug])
        response = self.client.get(url)
        self.assertEqual(response.data['id'], location.slug)

    def test_geojson_false_id_attribute_slug(self):
        location = Location.objects.create(
            name='falseid test', geometry='POINT (10.1 10.1)'
        )
        url = reverse('api_geojson_location_falseid_details', args=[location.id])
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], 'falseid test')
        with self.assertRaises(KeyError):
            response.data['id']

    def test_geojson_no_id_attribute_slug(self):
        location = Location.objects.create(
            name='noid test', geometry='POINT (10.1 10.1)'
        )
        url = reverse('api_geojson_location_noid_details', args=[location.id])
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], 'noid test')
        with self.assertRaises(KeyError):
            response.data['id']

    def test_geojson_filefield_attribute(self):
        located_file = LocatedFile.objects.create(
            name='geojson filefield test', geometry='POINT (10.1 10.1)'
        )
        url = reverse('api_geojson_located_file_details', args=[located_file.id])
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['file'], None)

    def test_post_geojson_location_list(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "type": "Feature",
            "properties": {"name": "point?", "details": "ignore this"},
            "geometry": {"type": "Point", "coordinates": [10.1, 10.1]},
        }
        response = self.client.post(
            self.geojson_location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        url = reverse(
            'api_geojson_location_details',
            args=[Location.objects.order_by('-id')[0].id],
        )
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], "point?")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(
            json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]"
        )
        self.assertNotEqual(response.data['properties']['details'], "ignore this")

    def test_post_geojson_location_list_HTML(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "type": "Feature",
            "properties": {"name": "point?", "details": "ignore this"},
            "geometry": {"type": "Point", "coordinates": [10.1, 10.1]},
        }
        response = self.client.post(
            self.geojson_location_list_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='text/html',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        url = reverse(
            'api_geojson_location_details',
            args=[Location.objects.order_by('-id')[0].id],
        )
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], "point?")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(
            json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]"
        )
        self.assertNotEqual(response.data['properties']['details'], "ignore this")

    def test_post_invalid_geojson_location_list(self):
        data = {
            "type": "Feature",
            "properties": {"details": "ignore this"},
            "geometry": {"type": "Point", "coordinates": [10.1, 10.1]},
        }
        response = self.client.post(
            self.geojson_location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(response.data['name'][0], "This field is required.")
        data = {
            "type": "Feature",
            "properties": {"name": "point?"},
            "geometry": {"type": "Point", "WRONG": {}},
        }
        response = self.client.post(
            self.geojson_location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(response.data['geometry'][0], self.gdal_error_message)

    def test_post_geojson_location_list_WKT(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "type": "Feature",
            "properties": {"name": "point?"},
            "geometry": "POINT (10.1 10.1)",
        }
        response = self.client.post(
            self.geojson_location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        url = reverse(
            'api_geojson_location_details',
            args=[Location.objects.order_by('-id')[0].id],
        )
        response = self.client.get(url)
        self.assertEqual(response.data['properties']['name'], "point?")
        self.assertEqual(response.data['geometry']['type'], "Point")
        self.assertEqual(
            json.dumps(response.data['geometry']['coordinates']), "[10.1, 10.1]"
        )

    def test_geofeatured_model_serializer_compatible_with_geomodel_serializer(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "name": "geojson input test",
            "geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point", "coordinates": [12.492324113849, 41.890307434153]}
                ],
            },
        }
        response = self.client.post(
            self.geojson_location_list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)

    def test_geofeatured_model_post_as_multipartformdata(self):
        """ emulate sending geojson string in webform """
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "name": "geojson input test",
            "geometry": json.dumps(
                {"type": "Point", "coordinates": [12.492324113849, 41.890307434153]}
            ),
        }
        response = self.client.post(self.location_list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(response.data['geometry']['type'], "Point")

    def test_HTML_browsable_geojson_location_list(self):
        response = self.client.get(
            self.geojson_location_list_url, HTTP_ACCEPT='text/html'
        )
        self.assertEqual(response.status_code, 200)
        self._create_locations()
        response = self.client.get(
            self.geojson_location_list_url, HTTP_ACCEPT='text/html'
        )
        self.assertContains(response, 'l1')
        self.assertContains(response, 'l2')

    def test_post_geojson_location_list_HTML_web_form(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {
            "name": "HTML test",
            "geometry": json.dumps({"type": "Point", "coordinates": [10.1, 10.1]}),
        }
        response = self.client.post(
            self.geojson_location_list_url, data, HTTP_ACCEPT='text/html'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        location = Location.objects.all()[0]
        self.assertEqual(location.name, "HTML test")
        self.assertEqual(location.geometry.geom_type, "Point")

    def test_post_geojson_location_list_HTML_web_form_WKT(self):
        self.assertEqual(Location.objects.count(), 0)
        data = {"name": "HTML test WKT", "geometry": "POINT (10.1 10.1)"}
        response = self.client.post(
            self.geojson_location_list_url, data, HTTP_ACCEPT='text/html'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)
        location = Location.objects.all()[0]
        self.assertEqual(location.name, "HTML test WKT")

    @skipIf(is_pre_drf_39, 'Skip this test if DRF < 3.9')
    def test_geojson_HTML_widget_value(self):
        self._create_locations()
        response = self.client.get(
            self.geojson_location_list_url, HTTP_ACCEPT='text/html'
        )
        self.assertContains(response, '<textarea name="geometry"')
        self.assertContains(response, '"type": "Point"')
        self.assertContains(response, '"coordinates": [')

    @skipIf(not is_pre_drf_39, 'Skip this test if DRF >= 3.9')
    def test_geojson_HTML_widget_value_pre_drf_39(self):
        self._create_locations()
        response = self.client.get(
            self.geojson_location_list_url, HTTP_ACCEPT='text/html'
        )
        self.assertContains(response, '<textarea name="geometry"')
        self.assertContains(response, '&quot;type&quot;: &quot;Point&quot;')
        self.assertContains(response, '&quot;coordinates&quot;: [')
        # TODO: remove this when python 2 will be deprecated
        self.assertNotContains(
            response, 'u&#39;type&#39;: u&#39;Point&#39;, u&#39;coordinates&#39;:'
        )

    def test_patch_geojson_location(self):
        location = Location.objects.create(
            name='geojson patch test', geometry='POINT (135.0 45.0)'
        )
        url = reverse('api_geojson_location_details', args=[location.id])
        data = {
            "properties": {"name": "geojson successful patch test"},
            "geometry": {"type": "Point", "coordinates": [10.1, 10.1]},
        }
        response = self.client.generic(
            'PATCH', url, json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        location_reloaded = Location.objects.get(pk=location.id)
        self.assertEquals(location_reloaded.name, 'geojson successful patch test')
        self.assertEquals(
            location_reloaded.geometry, Point(10.1, 10.1, srid=location.geometry.srid)
        )

    def test_patch_geojson_location_wo_changing_geometry(self):
        location = Location.objects.create(
            name='geojson patch test', geometry='POINT (135.0 45.0)'
        )
        url = reverse('api_geojson_location_details', args=[location.id])
        data = {"properties": {"name": "geojson successful patch test"}}
        response = self.client.generic(
            'PATCH', url, json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        location_reloaded = Location.objects.get(pk=location.id)
        self.assertEquals(location_reloaded.name, 'geojson successful patch test')
        self.assertEquals(
            location_reloaded.geometry, Point(135.0, 45.0, srid=location.geometry.srid)
        )

    def test_geometry_serializer_method_field(self):
        location = Location.objects.create(
            name='geometry serializer method test', geometry='POINT (135.0 45.0)'
        )
        location_loaded = Location.objects.get(pk=location.id)
        self.assertEqual(location_loaded.name, 'geometry serializer method test')
        self.assertEqual(
            location_loaded.geometry, Point(135.0, 45.0, srid=location.geometry.srid)
        )
        url = reverse('api_geojson_location_details_hidden', args=[location.id])
        data = {"properties": {"name": "hidden geometry"}}
        response = self.client.generic(
            'PATCH', url, json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['properties']['name'], 'hidden geometry')
        self.assertEqual(response.data['geometry']['type'], 'Point')
        self.assertEqual(response.data['geometry']['coordinates'], [0.0, 0.0])

    def test_geometry_serializer_method_field_none(self):
        location = Location.objects.create(
            name='None value', geometry='POINT (135.0 45.0)'
        )
        location_loaded = Location.objects.get(pk=location.id)
        self.assertEqual(
            location_loaded.geometry, Point(135.0, 45.0, srid=location.geometry.srid)
        )
        url = reverse('api_geojson_location_details_none', args=[location.id])
        response = self.client.generic('GET', url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['properties']['name'], 'None value')
        self.assertEqual(response.data['geometry'], None)

    def test_nullable_empty_geometry(self):
        empty = Nullable(name='empty', geometry='POINT EMPTY')
        empty.full_clean()
        empty.save()
        url = reverse('api_geojson_nullable_details', args=[empty.id])
        response = self.client.generic('GET', url, content_type='application/json')
        self.assertIsNotNone(response.data['geometry'])
        self.assertEqual(response.data['geometry']['coordinates'], [])

    def test_nullable_null_geometry(self):
        empty = Nullable(name='empty', geometry=None)
        empty.full_clean()
        empty.save()
        url = reverse('api_geojson_nullable_details', args=[empty.id])
        response = self.client.generic('GET', url, content_type='application/json')
        self.assertIsNone(response.data['geometry'])

    def test_geometry_field_to_representation_none(self):
        self._create_locations()
        f = LocationGeoSerializer(instance=self.l1).fields['geometry']
        self.assertIsNone(f.to_representation(None))

    def test_geometry_empty_representation(self):
        self._create_locations()
        f = LocationGeoSerializer(instance=self.l1).fields['geometry']
        geom_types = (
            'POINT',
            'LINESTRING',
            'LINEARRING',
            'POLYGON',
            'MULTIPOINT',
            'MULTILINESTRING',
            'MULTIPOLYGON',
        )
        for geom_type in geom_types:
            with self.subTest(geom_type=geom_type):
                value = f.to_representation(GEOSGeometry('{} EMPTY'.format(geom_type)))
                self.assertIsNotNone(value)
                if geom_type == 'LINEARRING':
                    geom_type = 'LINESTRING'
                self.assertEqual(value['type'].upper(), geom_type)
                self.assertEqual(value['coordinates'], [])
        # GEOMETRYCOLLECTION needs different handling
        value = f.to_representation(GEOSGeometry('GEOMETRYCOLLECTION EMPTY'))
        self.assertIsNotNone(value)
        self.assertEqual(value['type'].upper(), 'GEOMETRYCOLLECTION')
        self.assertEqual(value['geometries'], [])

    def test_no_geo_field_improperly_configured(self):
        class LocationGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
            class Meta:
                model = Location

        with self.assertRaises(ImproperlyConfigured):
            LocationGeoFeatureSerializer()

    def test_exclude_geo_field_improperly_configured(self):
        self._create_locations()

        class LocationGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
            class Meta:
                model = Location
                geo_field = 'geometry'
                exclude = ('geometry',)

        with self.assertRaises(ImproperlyConfigured):
            LocationGeoFeatureSerializer(instance=self.l1)

    def test_geojson_pagination(self):
        self._create_locations()
        response = self.client.get(self.geojson_location_list_url)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 2)
        response = self.client.get(
            '{0}?page_size=1'.format(self.geojson_location_list_url)
        )
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 1)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_pickle(self):
        geometry = GEOSGeometry('POINT (30 10)')
        geojsondict = GeoJsonDict(
            (('type', geometry.geom_type), ('coordinates', geometry.coords),)
        )
        pickled = pickle.dumps(geojsondict)
        restored = pickle.loads(pickled)
        self.assertEqual(restored, geojsondict)

    def test_geometrycollection_geojson(self):
        """ test geometry collection geojson behaviour """
        location = Location.objects.create(
            name='geometry collection geojson test',
            geometry='GEOMETRYCOLLECTION ('
            'POINT (135.0 45.0),'
            'LINESTRING (135.0 45.0,140.0 50.0,145.0 55.0),'
            'POLYGON ((135.0 45.0,140.0 50.0,145.0 55.0,135.0 45.0)))',
        )
        url = reverse('api_geojson_location_details', args=[location.id])
        expected = {
            'id': location.id,
            'type': 'Feature',
            'properties': {
                'details': "http://testserver/geojson/%s/" % location.id,
                'name': 'geometry collection geojson test',
                'fancy_name': 'Kool geometry collection geojson test',
                'timestamp': None,
                'slug': 'geometry-collection-geojson-test',
            },
            'geometry': {
                'type': 'GeometryCollection',
                'geometries': [
                    {'type': 'Point', 'coordinates': [135.0, 45.0]},
                    {
                        'type': 'LineString',
                        'coordinates': [[135.0, 45.0], [140.0, 50.0], [145.0, 55.0]],
                    },
                    {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [135.0, 45.0],
                                [140.0, 50.0],
                                [145.0, 55.0],
                                [135.0, 45.0],
                            ]
                        ],
                    },
                ],
            },
        }
        response = self.client.get(url)
        if sys.version_info > (3, 0, 0):
            self.assertCountEqual(json.dumps(response.data), json.dumps(expected))
        else:
            self.assertItemsEqual(json.dumps(response.data), json.dumps(expected))
        self.assertContains(response, "Kool geometry collection geojson test")
