from rest_framework import generics

from .models import *
from .serializers import *
from rest_framework_gis.filters import *


class LocationList(generics.ListCreateAPIView):
    model = Location
    serializer_class = LocationGeoSerializer
    pagination_serializer_class = PaginatedLocationGeoSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
location_list = LocationList.as_view()
    
    
class LocationDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoSerializer

location_details = LocationDetails.as_view()


class GeojsonLocationList(generics.ListCreateAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    pagination_serializer_class = PaginatedLocationGeoFeatureSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
geojson_location_list = GeojsonLocationList.as_view()


class GeojsonLocationContainedInBBoxList(generics.ListAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Location.objects.all()
    bbox_filter_field = 'geometry'
    filter_backends = (InBBOXFilter,)

geojson_location_contained_in_bbox_list = GeojsonLocationContainedInBBoxList.as_view()


class GeojsonLocationOverlapsBBoxList(GeojsonLocationContainedInBBoxList):
    bbox_filter_include_overlapping = True

geojson_location_overlaps_bbox_list = GeojsonLocationOverlapsBBoxList.as_view()


class GeojsonLocationDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer

geojson_location_details = GeojsonLocationDetails.as_view()


class GeojsonLocationSlugDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    lookup_field = 'slug'
    serializer_class = LocationGeoFeatureSlugSerializer

geojson_location_slug_details = GeojsonLocationSlugDetails.as_view()


class GeojsonLocationFalseIDDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureFalseIDSerializer

geojson_location_falseid_details = GeojsonLocationFalseIDDetails.as_view()
