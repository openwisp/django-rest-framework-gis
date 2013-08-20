from rest_framework import generics

from .models import *
from .serializers import *


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