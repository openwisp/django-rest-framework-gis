from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


__all__ = [
    'LocationGeoSerializer',
    'PaginatedLocationGeoSerializer',
    # GeoFeatureSerializer
    'LocationGeoFeatureSerializer',
    'PaginatedLocationGeoFeatureSerializer',
]

  
class LocationGeoSerializer(gis_serializers.GeoModelSerializer):
    """ location geo serializer  """
    
    #geometry = gis_serializers.GeometryField(required=True)
    
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
    
    class Meta:
        model = Location
        geo_field = 'geometry'


class PaginatedLocationGeoFeatureSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = LocationGeoFeatureSerializer