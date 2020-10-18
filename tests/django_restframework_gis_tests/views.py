from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from rest_framework_gis.filters import (
    DistanceToPointFilter,
    DistanceToPointOrderingFilter,
    GeoFilterSet,
    GeometryFilter,
    InBBoxFilter,
    TMSTileFilter,
)
from rest_framework_gis.pagination import GeoJsonPagination

from .models import BoxedLocation, LocatedFile, Location, Nullable
from .serializers import (
    BoxedLocationGeoFeatureSerializer,
    LocatedFileGeoFeatureSerializer,
    LocationGeoFeatureBboxSerializer,
    LocationGeoFeatureFalseIdSerializer,
    LocationGeoFeatureMethodSerializer,
    LocationGeoFeatureNoIdSerializer,
    LocationGeoFeatureSerializer,
    LocationGeoFeatureSlugSerializer,
    LocationGeoSerializer,
    NoneGeoFeatureMethodSerializer,
    PaginatedLocationGeoSerializer,
)


class LocationList(generics.ListCreateAPIView):
    model = Location
    serializer_class = LocationGeoSerializer
    queryset = Location.objects.all()
    pagination_class = PaginatedLocationGeoSerializer


location_list = LocationList.as_view()


class LocationDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoSerializer
    queryset = Location.objects.all()


location_details = LocationDetails.as_view()


class GeojsonLocationList(generics.ListCreateAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Location.objects.all()
    pagination_class = GeoJsonPagination


geojson_location_list = GeojsonLocationList.as_view()


class GeojsonLocationContainedInBBoxList(generics.ListAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Location.objects.all()
    bbox_filter_field = 'geometry'
    filter_backends = (InBBoxFilter,)


geojson_location_contained_in_bbox_list = GeojsonLocationContainedInBBoxList.as_view()


class GeojsonLocationOverlapsBBoxList(GeojsonLocationContainedInBBoxList):
    bbox_filter_include_overlapping = True


geojson_location_overlaps_bbox_list = GeojsonLocationOverlapsBBoxList.as_view()


class GeojsonLocationContainedInTileList(generics.ListAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Location.objects.all()
    bbox_filter_field = 'geometry'
    filter_backends = (TMSTileFilter,)


geojson_location_contained_in_tile_list = GeojsonLocationContainedInTileList.as_view()


class GeojsonLocationOverlapsTileList(GeojsonLocationContainedInTileList):
    bbox_filter_include_overlapping = True


geojson_location_overlaps_tile_list = GeojsonLocationOverlapsTileList.as_view()


class GeojsonLocationWithinDistanceOfPointList(generics.ListAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    distance_filter_convert_meters = True
    queryset = Location.objects.all()
    distance_filter_field = 'geometry'
    filter_backends = (DistanceToPointFilter,)


geojson_location_within_distance_of_point_list = (
    GeojsonLocationWithinDistanceOfPointList.as_view()
)


class GeojsonLocationWithinDegreesOfPointList(GeojsonLocationWithinDistanceOfPointList):
    distance_filter_convert_meters = False  # Default setting


geojson_location_within_degrees_of_point_list = (
    GeojsonLocationWithinDegreesOfPointList.as_view()
)


class GeojsonLocationOrderDistanceToPointList(generics.ListAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Location.objects.all()
    distance_ordering_filter_field = 'geometry'
    filter_backends = (DistanceToPointOrderingFilter,)


geojson_location_order_distance_to_point_list = (
    GeojsonLocationOrderDistanceToPointList.as_view()
)


class GeojsonLocationDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Location.objects.all()


geojson_location_details = GeojsonLocationDetails.as_view()


class GeojsonLocationDetailsHidden(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureMethodSerializer
    queryset = Location.objects.all()


geojson_location_details_hidden = GeojsonLocationDetailsHidden.as_view()


class GeojsonLocationDetailsNone(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = NoneGeoFeatureMethodSerializer
    queryset = Location.objects.all()


geojson_location_details_none = GeojsonLocationDetailsNone.as_view()


class GeojsonLocationSlugDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    lookup_field = 'slug'
    serializer_class = LocationGeoFeatureSlugSerializer
    queryset = Location.objects.all()


geojson_location_slug_details = GeojsonLocationSlugDetails.as_view()


class GeojsonLocationFalseIdDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureFalseIdSerializer
    queryset = Location.objects.all()


geojson_location_falseid_details = GeojsonLocationFalseIdDetails.as_view()


class GeojsonLocationNoIdDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureNoIdSerializer
    queryset = Location.objects.all()


geojson_location_noid_details = GeojsonLocationNoIdDetails.as_view()


class LocationFilter(GeoFilterSet):
    contains_properly = GeometryFilter(
        field_name='geometry', lookup_expr='contains_properly'
    )

    class Meta:
        model = Location
        fields = ['contains_properly']


class GeojsonLocationContainedInGeometry(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationGeoSerializer
    filter_class = LocationFilter

    filter_backends = (DjangoFilterBackend,)


geojson_contained_in_geometry = GeojsonLocationContainedInGeometry.as_view()


class GeojsonLocatedFileDetails(generics.RetrieveUpdateDestroyAPIView):
    model = LocatedFile
    serializer_class = LocatedFileGeoFeatureSerializer
    queryset = LocatedFile.objects.all()


geojson_located_file_details = GeojsonLocatedFileDetails.as_view()


class GeojsonBoxedLocationDetails(generics.RetrieveUpdateDestroyAPIView):
    model = BoxedLocation
    serializer_class = BoxedLocationGeoFeatureSerializer
    queryset = BoxedLocation.objects.all()


geojson_boxedlocation_details = GeojsonBoxedLocationDetails.as_view()


class GeojsonBoxedLocationList(generics.ListCreateAPIView):
    model = BoxedLocation
    serializer_class = BoxedLocationGeoFeatureSerializer
    queryset = BoxedLocation.objects.all()


geojson_boxedlocation_list = GeojsonBoxedLocationList.as_view()


class GeojsonLocationBboxList(generics.ListCreateAPIView):
    model = Location
    serializer_class = LocationGeoFeatureBboxSerializer
    queryset = Location.objects.all()


geojson_location_bbox_list = GeojsonLocationBboxList.as_view()


class GeojsonNullableDetails(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    serializer_class = LocationGeoFeatureSerializer
    queryset = Nullable.objects.all()


geojson_nullable_details = GeojsonNullableDetails.as_view()
