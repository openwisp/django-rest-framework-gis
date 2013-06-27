django-rest-framework-gis
=========================

Geographic add-ons for Django Rest Framework

Fields
------

Provides a GeometryField, which is a subclass of DRF WritableField. 
This field handles GeoDjango geometry fields, providing custom to_native 
and from_native methods for GeoJSON input/output.

Serializers
-----------

Provides a GeoModelSerializer, which is a sublass os DRF ModelSerializer.
This serializer updates the field_mapping dictionary to include
field mapping of GeoDjango geometry fields to the above GeometryField.

For example, the following model::

class Location(models.Model):
    """
    A model which holds information about a particular location
   """
   address = models.Charfield(max_length=255)
   city = models.CharField(max_length=100)
   state = models.CharField(max_length=100)
   point = models.PointField()

By default, the DRF ModelSerializer will output::

{
     "id": 1, 
     "address": "742 Evergreen Terrace", 
      "city":  "Springfield", 
      "state": "Oregon",
      "point": "POINT(-123.0208 44.0464)" 
}

In contrast, the GeoModelSerizalizer will output::

{
     "id": 1, 
     "address": "742 Evergreen Terrace", 
      "city":  "Springfield", 
      "state": "Oregon",
      "point": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464],
       },
}

Note that this output is still JSON and not properly formatted GeoJSON.
Further development needs to be done to output GeoJSON. 


Filters
-------

Provides a InBBOXFilter, which is a subclass of DRF BaseFilerBackend.
Filters a queryset to only those instance within a certain bounding box.

