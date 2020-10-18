from django.contrib import admin
from django.contrib.gis.admin import ModelAdmin as GeoModelAdmin

from .models import Location


class LocationAdmin(GeoModelAdmin):
    list_display = ('name', 'geometry')


admin.site.register(Location, LocationAdmin)
