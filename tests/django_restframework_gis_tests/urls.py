from django.conf.urls import patterns, url


urlpatterns = patterns('django_restframework_gis_tests.views',
    url(r'^$', 'location_list', name='api_location_list'),
    url(r'^(?P<pk>[0-9]+)/$', 'location_details', name='api_location_details'),
    
    # geojson
    url(r'^geojson/$', 'geojson_location_list', name='api_geojson_location_list'),
    url(r'^geojson/(?P<pk>[0-9]+)/$', 'geojson_location_details', name='api_geojson_location_details'),
)