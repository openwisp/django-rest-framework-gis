from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.location_list, name='api_location_list'),
    url(
        r'^(?P<pk>[0-9]+)/$',
        views.location_details,
        name='api_location_details'),

    # geojson
    url(
        r'^geojson/$',
        views.geojson_location_list,
        name='api_geojson_location_list'),
    url(
        r'^geojson/(?P<pk>[0-9]+)/$',
        views.geojson_location_details,
        name='api_geojson_location_details'),
    url(
        r'^geojson-nullable/(?P<pk>[0-9]+)/$',
        views.geojson_nullable_details,
        name='api_geojson_nullable_details'),
    url(
        r'^geojson_hidden/(?P<pk>[0-9]+)/$',
        views.geojson_location_details_hidden,
        name='api_geojson_location_details_hidden'),
    url(
        r'^geojson_none/(?P<pk>[0-9]+)/$',
        views.geojson_location_details_none,
        name='api_geojson_location_details_none'),
    url(
        r'^geojson/(?P<slug>[-\w]+)/$',
        views.geojson_location_slug_details,
        name='api_geojson_location_slug_details'),
    url(
        r'^geojson-falseid/(?P<pk>[0-9]+)/$',
        views.geojson_location_falseid_details,
        name='api_geojson_location_falseid_details'),
    url(
        r'^geojson-noid/(?P<pk>[0-9]+)/$',
        views.geojson_location_noid_details,
        name='api_geojson_location_noid_details'),

    # file
    url(
        r'^geojson-file/(?P<pk>[0-9]+)/$',
        views.geojson_located_file_details,
        name='api_geojson_located_file_details'),

    # geojson with bbox with its own geometry field
    url(
        r'^geojson-with-bbox/$',
        views.geojson_boxedlocation_list,
        name='api_geojson_boxedlocation_list'),
    url(
        r'^geojson-with-bbox/(?P<pk>[0-9]+)/$',
        views.geojson_boxedlocation_details,
        name='api_geojson_boxedlocation_details'),

    # geojson with bbox with autogenerated bbox
    url(
        r'^geojson-with-auto-bbox/$',
        views.geojson_location_bbox_list,
        name='api_geojson_location_bbox_list'),

    # Filters
    url(
        r'^filters/contained_in_bbox$',
        views.geojson_location_contained_in_bbox_list,
        name='api_geojson_location_list_contained_in_bbox_filter'),
    url(
        r'^filters/overlaps_bbox$',
        views.geojson_location_overlaps_bbox_list,
        name='api_geojson_location_list_overlaps_bbox_filter'),
    url(
        r'^filters/contained_in_geometry$',
        views.geojson_contained_in_geometry,
        name='api_geojson_contained_in_geometry'),
    url(
        r'^filters/contained_in_tile$',
        views.geojson_location_contained_in_tile_list,
        name='api_geojson_location_list_contained_in_tile_filter'),
    url(
        r'^filters/overlaps_tile$',
        views.geojson_location_overlaps_tile_list,
        name='api_geojson_location_list_overlaps_tile_filter'),
    url(
        r'^filters/within_distance_of_point$',
        views.geojson_location_within_distance_of_point_list,
        name='api_geojson_location_list_within_distance_of_point_filter'),
    url(
        r'^filters/within_degrees_of_point$',
        views.geojson_location_within_degrees_of_point_list,
        name='api_geojson_location_list_within_degrees_of_point_filter'),
    url(
        r'^filters/order_distance_to_point$',
        views.geojson_location_order_distance_to_point_list,
        name='api_geojson_location_order_distance_to_point_list_filter'),
]
