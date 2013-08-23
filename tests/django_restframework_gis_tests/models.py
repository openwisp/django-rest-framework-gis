from django.contrib.gis.db import models


__all__ = ['Location']


class Location(models.Model):
    name = models.CharField(max_length=32)
    geometry = models.GeometryField()
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
