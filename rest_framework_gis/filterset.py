from django.contrib.gis.db import models
from django.contrib.gis.db.models.sql.query import ALL_TERMS

from django_filters import FilterSet

from .filters import GeometryFilter

class GeoFilterSet(FilterSet):
    GEOFILTER_FOR_DBFIELD_DEFAULTS = {
        models.GeometryField: {
            'filter_class': GeometryFilter
        },
    }

    def __new__(cls, *args, **kwargs):
        cls.filter_overrides.update(cls.GEOFILTER_FOR_DBFIELD_DEFAULTS)
        cls.LOOKUP_TYPES = sorted(ALL_TERMS)
        return super(GeoFilterSet, cls).__new__(cls)
