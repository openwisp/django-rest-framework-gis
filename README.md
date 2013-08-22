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

__GeoModelSerializer__

Provides a GeoModelSerializer, which is a sublass of DRF ModelSerializer.
This serializer updates the field_mapping dictionary to include
field mapping of GeoDjango geometry fields to the above GeometryField.

For example, the following model:

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
    
    
__GeoFeatureModelSerializer__

GeoFeatureModelSerializer is a subclass of GeoModelSerializer which will output data in a format that is GeoJSON
compatible. Using the above example, the GeoFeatureModelSerializer will output:

     {
        "type": "Feature",
        "properties": {
            "id": 1, 
            "address": "742 Evergreen Terrace", 
            "city":  "Springfield", 
            "state": "Oregon",
        }
        "geometry": {
            "point": {
                "type": "Point",
                "coordinates": [-123.0208, 44.0464],
            },
        },
    }
    
If you are serializing an object list, GeoFeatureModelSerializer will create a FeatureCollection:

[ NOTE: This currenty does not work with the default pagination serializer ]

    { 
        "type": "FeatureCollection",
        "features": [
        {
            "type": "Feature",
            "properties": {
                "id": 1, 
                "address": "742 Evergreen Terrace", 
                "city":  "Springfield", 
                "state": "Oregon",
            }
            "geometry": {
                "point": {
                    "type": "Point",
                    "coordinates": [-123.0208, 44.0464],
                },
            },
        }
        {
            "type": "Feature",
            "properties": {
                "id": 2, 
                "address": "744 Evergreen Terrace", 
                "city":  "Springfield", 
                "state": "Oregon",
            }
            "geometry": {
                "point": {
                    "type": "Point",
                    "coordinates": [-123.0208, 44.0489],
                },
            },
        }
    }
    
GeoFeatureModelSerializer requires you to define a "geo_field" to be serialized as the "geometry". For example:

    class LocationSerializer(GeoFeatureModelSerializer):
        """ A class to serialize locations as GeoJSON compatible data """
        
        class Meta:
            model = Location
            geo_field = "point"
        
            # you can also explicitly declare which fields you want to include
            # as with a ModelSerializer.
            fields = ('address', 'city', 'state')
            


Filters
-------

Provides a InBBOXFilter, which is a subclass of DRF BaseFilterBackend.
Filters a queryset to only those instances within a certain bounding box.


Running the tests
-----------------

Assuming one has the dependencies installed (restframework and restframework_gis),
and one of the **Sptial Database server supported by GeoDjango** is up and running::

    python setup.py test

You might need to tweak the DB settings according to your DB configuration.
You can copy the file local_settings.example.py to **local_settings.py** and change
the DATABASES and/or INSTALLED_APPS directive there.

**Warning**: tests are still a work in progress.

Contributing to the tests
-------------------------

If you want to contribute you need to install the test app in a proper development environment.

These steps should do:
 * create a spatial database named "django_restframework_gis"
 * create local_settings.py, eg: `cp local_settings.example.py local_settings.py`
 * tweak the DATABASES configuration directive according to your DB
 * optionally install olwidget (pip install olwidget)
 * uncomment INSTALLED_APPS (remove olwidget if you did not install it)
 * run `python manage.py syncdb`
 * run `python manage.py collectstatic`
 * run `python manage.py runserver`