from django.contrib.gis.geos import Point

from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


__all__ = [
    'LocationGeoSerializer',
    'PaginatedLocationGeoSerializer',
    'LocationGeoFeatureSerializer',
    'LocationGeoFeatureSlugSerializer',
    'LocationGeoFeatureFalseIdSerializer',
    'LocationGeoFeatureNoIdSerializer',
    'LocatedFileGeoFeatureSerializer',
    'BoxedLocationGeoFeatureSerializer',
    'LocationGeoFeatureBboxSerializer',
    'LocationGeoFeatureMethodSerializer',
    'NoneGeoFeatureMethodSerializer',
]


class LocationGeoSerializer(serializers.ModelSerializer):
    """ location geo serializer  """
    details = serializers.HyperlinkedIdentityField(view_name='api_location_details')

    class Meta:
        model = Location
        fields = '__all__'


class PaginatedLocationGeoSerializer(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 40
    max_page_size = 10000


class LocationGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ location geo serializer  """
    details = serializers.HyperlinkedIdentityField(view_name='api_geojson_location_details')
    fancy_name = serializers.SerializerMethodField()

    def get_fancy_name(self, obj):
        return 'Kool %s' % obj.name

    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = '__all__'


class LocationGeoFeatureSlugSerializer(LocationGeoFeatureSerializer):
    """ use slug as id attribute  """
    class Meta:
        model = Location
        geo_field = 'geometry'
        id_field = 'slug'
        fields = ('name', 'slug', 'timestamp')


class LocationGeoFeatureFalseIdSerializer(LocationGeoFeatureSerializer):
    """ id attribute set as False """
    class Meta:
        model = Location
        geo_field = 'geometry'
        id_field = False
        fields = '__all__'


class LocationGeoFeatureNoIdSerializer(LocationGeoFeatureSerializer):
    """
    id attribute left out, issue #82
    see: https://github.com/djangonauts/django-rest-framework-gis/issues/82
    """
    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = ('name',)


class LocatedFileGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ located file geo serializer  """
    details = serializers.HyperlinkedIdentityField(view_name='api_geojson_located_file_details')
    fancy_name = serializers.SerializerMethodField()
    file = serializers.FileField(allow_empty_file=True)

    def get_fancy_name(self, obj):
        return 'Nice %s' % obj.name

    class Meta:
        model = Location
        geo_field = 'geometry'
        exclude = []


class BoxedLocationGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ location geo serializer  """
    details = serializers.HyperlinkedIdentityField(view_name='api_geojson_boxedlocation_details')

    class Meta:
        model = BoxedLocation
        geo_field = 'geometry'
        bbox_geo_field = 'bbox_geometry'
        fields = ['name', 'details', 'id', 'timestamp']


class LocationGeoFeatureBboxSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'geometry'
        auto_bbox = True
        exclude = []


class LocationGeoFeatureMethodSerializer(gis_serializers.GeoFeatureModelSerializer):
    new_geometry = gis_serializers.GeometrySerializerMethodField()

    def get_new_geometry(self, obj):
        if obj.name.startswith('hidden'):
            return Point(0., 0.)
        else:
            return obj.geometry

    class Meta:
        model = Location
        geo_field = 'new_geometry'
        exclude = []


class NoneGeoFeatureMethodSerializer(gis_serializers.GeoFeatureModelSerializer):
    new_geometry = gis_serializers.GeometrySerializerMethodField()

    def get_new_geometry(self, obj):
        return None

    class Meta:
        model = Location
        geo_field = 'new_geometry'
        fields = ['name', 'slug', 'id']
