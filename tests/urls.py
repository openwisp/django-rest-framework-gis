from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import include, path

urlpatterns = [
    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url('admin/doc/', include('django.contrib.admindocs.urls')),
    path('', include('django_restframework_gis_tests.urls')),
    path('static/<path>', views.serve),
]
