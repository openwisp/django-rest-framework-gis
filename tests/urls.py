try:
    from django.urls import include, url
except ImportError:
    from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles import views

urlpatterns = [
    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'', include('django_restframework_gis_tests.urls')),
    url(r'^static/(?P<path>.*)$', views.serve),
]
