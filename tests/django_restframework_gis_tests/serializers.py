from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


__all__ = [
    'LocationGeoSerializer',
    'PaginatedLocationGeoSerializer',
    'LocationGeoFeatureSerializer',
    'LocationGeoFeatureSlugSerializer',
    'LocationGeoFeatureFalseIDSerializer',
    'PaginatedLocationGeoFeatureSerializer',
]

  
class LocationGeoSerializer(gis_serializers.GeoModelSerializer):
    """ location geo serializer  """
    
    details = serializers.HyperlinkedIdentityField(view_name='api_location_details')
    
    class Meta:
        model = Location
        geo_field = 'geometry'


class PaginatedLocationGeoSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = LocationGeoSerializer


class LocationGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ location geo serializer  """
    
    details = serializers.HyperlinkedIdentityField(view_name='api_geojson_location_details')
    fancy_name = serializers.SerializerMethodField('get_fancy_name')
    
    def get_fancy_name(self, obj):
        return u'Kool %s' % obj.name
    
    class Meta:
        model = Location
        geo_field = 'geometry'


class LocationGeoFeatureSlugSerializer(LocationGeoFeatureSerializer):
    """ use slug as id attribute  """
    
    class Meta:
        model = Location
        geo_field = 'geometry'
        id_field = 'slug'


class LocationGeoFeatureFalseIDSerializer(LocationGeoFeatureSerializer):
    """ id attribute set as False """
    
    class Meta:
        model = Location
        geo_field = 'geometry'
        id_field = False


class PaginatedLocationGeoFeatureSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = LocationGeoFeatureSerializer
