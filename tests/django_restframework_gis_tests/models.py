from django.contrib.gis.db import models
from django.utils.text import slugify


__all__ = ['Location', 'LocatedFile', 'LocatedImage']


class Location(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    geometry = models.GeometryField()
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
    def _generate_slug(self):
        if self.slug == '' or self.slug is None:
            try:
                name = unicode(self.name)
            except NameError:
                name = self.name
            self.slug = slugify(name)
    
    def clean(self):
        self._generate_slug()
    
    def save(self, *args, **kwargs):
        self._generate_slug()
        super(Location, self).save(*args, **kwargs)


class LocatedFile(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    file = models.FileField(upload_to='located_files', blank=True, null=True)
    geometry = models.GeometryField()

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    def _generate_slug(self):
        if self.slug == '' or self.slug is None:
            try:
                name = unicode(self.name)
            except NameError:
                name = self.name
            self.slug = slugify(name)

    def clean(self):
        self._generate_slug()

    def save(self, *args, **kwargs):
        self._generate_slug()
        super(LocatedFile, self).save(*args, **kwargs)


class LocatedImage(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    image = models.ImageField(upload_to='located_images', blank=True, null=True)
    geometry = models.GeometryField()

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    def _generate_slug(self):
        if self.slug == '' or self.slug is None:
            try:
                name = unicode(self.name)
            except NameError:
                name = self.name
            self.slug = slugify(name)

    def clean(self):
        self._generate_slug()

    def save(self, *args, **kwargs):
        self._generate_slug()
        super(LocatedImage, self).save(*args, **kwargs)
