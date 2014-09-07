from django.conf.urls import patterns, url


urlpatterns = patterns('django_restframework_gis_tests.views',
    url(r'^$', 'location_list', name='api_location_list'),
    url(r'^(?P<pk>[0-9]+)/$', 'location_details', name='api_location_details'),
    
    # geojson
    url(r'^geojson/$', 'geojson_location_list', name='api_geojson_location_list'),
    url(r'^geojson/(?P<pk>[0-9]+)/$', 'geojson_location_details', name='api_geojson_location_details'),
    url(r'^geojson/(?P<slug>[-\w]+)/$', 'geojson_location_slug_details', name='api_geojson_location_slug_details'),
    url(r'^geojson-falseid/(?P<pk>[0-9]+)/$', 'geojson_location_falseid_details', name='api_geojson_location_falseid_details'),
    
    # Filters
    url(r'^filters/contained_in_bbox$', 'geojson_location_contained_in_bbox_list', name='api_geojson_location_list_contained_in_bbox_filter'),
    url(r'^filters/overlaps_bbox$', 'geojson_location_overlaps_bbox_list', name='api_geojson_location_list_overlaps_bbox_filter'),
    url(r'^filters/contained_in_geometry$', 'geojson_contained_in_geometry', name='api_geojson_contained_in_geometry'),
    url(r'^filters/contained_in_tile$', 'geojson_location_contained_in_tile_list', name='api_geojson_location_list_contained_in_tile_filter'),
    url(r'^filters/overlaps_tile$', 'geojson_location_overlaps_tile_list', name='api_geojson_location_list_overlaps_tile_filter'),
    url(r'^filters/within_distance_of_point$', 'geojson_location_within_distance_of_point_list', name='api_geojson_location_list_within_distance_of_point_filter'),
    url(r'^filters/within_degrees_of_point$', 'geojson_location_within_degrees_of_point_list', name='api_geojson_location_list_within_degrees_of_point_filter'),
)
