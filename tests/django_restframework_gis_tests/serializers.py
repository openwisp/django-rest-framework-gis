from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


__all__ = [
    'LocationGeoSerializer',
    'PaginatedLocationGeoSerializer',
]

  
class LocationGeoSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ location geo serializer  """
    
    details = serializers.HyperlinkedIdentityField(view_name='api_location_details')
    
    class Meta:
        model = Location
        geo_field = 'geometry'


class PaginatedLocationGeoSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = LocationGeoSerializer