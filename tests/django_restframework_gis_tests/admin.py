from django.contrib import admin
from django.conf import settings

GEODJANGO_IMPROVED_WIDGETS = 'olwidget' in settings.INSTALLED_APPS

if GEODJANGO_IMPROVED_WIDGETS:
    from olwidget.admin import GeoModelAdmin
else:
    from django.contrib.gis.admin import ModelAdmin as GeoModelAdmin

from .models import Location


class LocationAdmin(GeoModelAdmin):
    list_display = ('name', 'geometry')


admin.site.register(Location, LocationAdmin)