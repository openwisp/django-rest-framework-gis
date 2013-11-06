from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    url(r'', include('django_restframework_gis_tests.urls')),
    
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve'),
)
