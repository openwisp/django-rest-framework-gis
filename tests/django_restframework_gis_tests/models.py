from django.contrib.gis.db import models
from django.utils.text import slugify

__all__ = ['Location', 'LocatedFile', 'BoxedLocation', 'Nullable']


class BaseModel(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    geometry = models.GeometryField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def _generate_slug(self):
        if self.slug == '' or self.slug is None:
            try:
                name = str(self.name)
            except NameError:
                name = self.name
            self.slug = slugify(name)

    def clean(self):
        self._generate_slug()

    def save(self, *args, **kwargs):
        self._generate_slug()
        super().save(*args, **kwargs)


class Location(BaseModel):
    pass


class LocatedFile(BaseModel):
    file = models.FileField(upload_to='located_files', blank=True, null=True)


class BoxedLocation(BaseModel):
    bbox_geometry = models.PolygonField()


class Nullable(BaseModel):
    geometry = models.GeometryField(blank=True, null=True)
