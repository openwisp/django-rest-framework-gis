django-rest-framework-gis
=========================

|Build Status| |Coverage Status| |Code Health| |PyPI version|
|Requirements Status|

Geographic add-ons for Django Rest Framework - `Mailing
List <https://groups.google.com/forum/#!forum/django-rest-framework-gis>`__.

Install
-------

.. code-block:: bash

    pip install djangorestframework-gis

Django Rest Framework Compatibility
-----------------------------------

===============================  ============================
djangorestframework-gis version  djangorestframework version
**0.3.0**                        higher than **2.3.14**
**0.2.0**                        from **2.2.2** to **2.3.13**
===============================  ============================

Fields
------

Provides a GeometryField, which is a subclass of Django Rest Framework
(from now on **DRF**) ``WritableField``. This field handles GeoDjango
geometry fields, providing custom ``to_native`` and ``from_native``
methods for GeoJSON input/output.

Serializers
-----------

GeoModelSerializer
~~~~~~~~~~~~~~~~~~

Provides a ``GeoModelSerializer``, which is a sublass of DRF
``ModelSerializer``. This serializer updates the field\_mapping
dictionary to include field mapping of GeoDjango geometry fields to the
above ``GeometryField``.

For example, the following model:

.. code-block:: python

    class Location(models.Model):
        """
        A model which holds information about a particular location
        """
        address = models.Charfield(max_length=255)
        city = models.CharField(max_length=100)
        state = models.CharField(max_length=100)
        point = models.PointField()

By default, the DRF ModelSerializer will output:

.. code-block:: javascript

    {
        "id": 1,
        "address": "742 Evergreen Terrace",
        "city":  "Springfield",
        "state": "Oregon",
        "point": "POINT(-123.0208 44.0464)"
    }

In contrast, the ``GeoModelSerizalizer`` will output:

.. code-block:: javascript

    {
        "id": 1,
        "address": "742 Evergreen Terrace",
        "city":  "Springfield",
        "state": "Oregon",
        "point": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464],
        }
    }

GeoFeatureModelSerializer
~~~~~~~~~~~~~~~~~~~~~~~~~

``GeoFeatureModelSerializer`` is a subclass of ``GeoModelSerializer``
which will output data in a format that is **GeoJSON** compatible. Using
the above example, the ``GeoFeatureModelSerializer`` will output:

.. code-block:: javascript

     {
        "id": 1,
        "type": "Feature",
        "geometry": {
            "point": {
                "type": "Point",
                "coordinates": [-123.0208, 44.0464],
            },
        },
        "properties": {
            "address": "742 Evergreen Terrace",
            "city":  "Springfield",
            "state": "Oregon"
        }
    }

If you are serializing an object list, ``GeoFeatureModelSerializer``
will create a ``FeatureCollection``:

(**NOTE:** This currenty does not work with the default pagination
serializer)

.. code-block:: javascript

    {
        "type": "FeatureCollection",
        "features": [
        {
            "id": 1
            "type": "Feature",
            "geometry": {
                "point": {
                    "type": "Point",
                    "coordinates": [-123.0208, 44.0464],
                }
            },
            "properties": {
                "address": "742 Evergreen Terrace",
                "city":  "Springfield",
                "state": "Oregon",
            }
        }
        {
            "id": 2,
            "type": "Feature",
            "geometry": {
                "point": {
                    "type": "Point",
                    "coordinates": [-123.0208, 44.0489],
                },
            },
            "properties": {
                "address": "744 Evergreen Terrace",
                "city":  "Springfield",
                "state": "Oregon"
            }
        }
    }

``GeoFeatureModelSerializer`` requires you to define a **``geo_field``**
to be serialized as the "geometry". For example:

.. code-block:: python

    class LocationSerializer(GeoFeatureModelSerializer):
        """ A class to serialize locations as GeoJSON compatible data """

        class Meta:
            model = Location
            geo_field = "point"

            # you can also explicitly declare which fields you want to include
            # as with a ModelSerializer.
            fields = ('id', 'address', 'city', 'state')

The primary key of the model (usually the "id" attribute) is
automatically put outside the "properties" object (before "type") unless
**``id_field``** is set to False:

.. code-block:: python

    class LocationSerializer(GeoFeatureModelSerializer):

        class Meta:
            model = Location
            geo_field = "point"
            id_field = False
            fields = ('id', 'address', 'city', 'state')

You could also set the **``id_field``** to some other unique field in
your model, like **"slug"**:

.. code-block:: python

    class LocationSerializer(GeoFeatureModelSerializer):

        class Meta:
            model = Location
            geo_field = "point"
            id_field = "slug"
            fields = ('slug', 'address', 'city', 'state')

Filters
-------

We provide a ``GeometryFilter`` field as well as a ``GeoFilterSet``
for usage with ``django_filter``. You simply provide, in the query
string, one of the textual types supported by ``GEOSGeometry``. By
default, this includes WKT, HEXEWKB, WKB (in a buffer), and GeoJSON.

GeometryFilter
~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework_gis.filterset import GeoFilterSet

    class RegionFilter(GeoFilterSet):
        slug = filters.CharFilter(name='slug', lookup_type='istartswith')
        contains_geom = filters.GeometryFilter(name='geom', lookup_type='contains')

        class Meta:
            model = Region

We can then filter in the URL, using GeoJSON, and we will perform a
``__contains`` geometry lookup, e.g.
``/region/?contains_geom={ "type": "Point", "coordinates": [ -123.26436996459961, 44.564178042345375 ] }``.

GeoFilterSet
~~~~~~~~~~~~

The ``GeoFilterSet`` provides a ``django_filter`` compatible
``FilterSet`` that will automatically create ``GeometryFilters`` for
``GeometryFields``.

InBBOXFilter
~~~~~~~~~~~~

Provides a ``InBBOXFilter``, which is a subclass of DRF
``BaseFilterBackend``. Filters a queryset to only those instances within
a certain bounding box.


``views.py:``

.. code-block:: python

    from rest_framework_gis.filters import InBBOXFilter

    class LocationList(ListAPIView):

        queryset = models.Location.objects.all()
        serializer_class = serializers.LocationSerializer
        bbox_filter_field = 'point'
        filter_backends = (InBBOXFilter, ) 
        bbox_filter_include_overlapping = True # Optional

We can then filter in the URL, using Bounding Box format (min Lon, min 
Lat, max Lon, max Lat), and we can search for instances within the 
bounding box, e.g.:
``/location/?in_bbox=-90,29,-89,35``.

By default, InBBOXFilter will only return those instances entirely 
within the stated bounding box. To include those instances which overlap 
the bounding box, include ``bbox_filter_include_overlapping = True`` 
in your view.

Note that if you are using other filters, you'll want to include your 
other filter backend in your view. For example:

``filter_backends = (InBBOXFilter, DjangoFilterBackend,)``

Projects using this package
--------------------------

- `Nodeshot <https://github.com/ninuxorg/nodeshot>`__: Extensible Django web application for management of community-led georeferenced data

Running the tests
-----------------

Assuming one has the dependencies installed (restframework and
restframework\_gis), and one of the `Spatial Database server supported
by
GeoDjango <https://docs.djangoproject.com/en/dev/ref/contrib/gis/db-api/#module-django.contrib.gis.db.backends>`__
is up and running:

.. code-block:: bash

    ./runtests.py

You might need to tweak the DB settings according to your DB
configuration. You can copy the file ``local_settings.example.py`` to
``local_settings.py`` and change the ``DATABASES`` and/or
``INSTALLED_APPS`` directives there.

If you want to contribute you need to install the test app in a proper
development environment.

These steps should do the trick:

-  create a spatial database named "django\_restframework\_gis"
-  create ``local_settings.py``, eg:
   ``cp local_settings.example.py local_settings.py``
-  tweak the ``DATABASES`` configuration directive according to your DB
   settings
-  optionally install ``olwidget`` with ``pip install olwidget``
-  uncomment ``INSTALLED_APPS`` (remove olwidget if you did not install
   it)
-  run ``python manage.py syncdb``
-  run ``python manage.py collectstatic``
-  run ``python manage.py runserver``

Contributing
------------

1. Join the `Django REST Framework GIS Mailing
   List <https://groups.google.com/forum/#!forum/django-rest-framework-gis>`__
   and announce your intentions
2. Follow the `PEP8 Style Guide for Python
   Code <http://www.python.org/dev/peps/pep-0008/>`__
3. Fork this repo
4. Write code
5. Write tests for your code
6. Ensure all tests pass
7. Ensure test coverage is not under 90%
8. Document your changes
9. Send pull request

.. |Build Status| image:: https://travis-ci.org/djangonauts/django-rest-framework-gis.png?branch=master
   :target: https://travis-ci.org/djangonauts/django-rest-framework-gis
.. |Coverage Status| image:: https://coveralls.io/repos/djangonauts/django-rest-framework-gis/badge.png
   :target: https://coveralls.io/r/djangonauts/django-rest-framework-gis
.. |Code Health| image:: https://landscape.io/github/djangonauts/django-rest-framework-gis/master/landscape.png
   :target: https://landscape.io/github/djangonauts/django-rest-framework-gis/master
.. |PyPI version| image:: https://badge.fury.io/py/djangorestframework-gis.png
   :target: http://badge.fury.io/py/djangorestframework-gis
.. |Requirements Status| image:: https://requires.io/github/djangonauts/django-rest-framework-gis/requirements.png?branch=master
   :target: https://requires.io/github/djangonauts/django-rest-framework-gis/requirements/?branch=master