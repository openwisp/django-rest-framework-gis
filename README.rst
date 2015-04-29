django-rest-framework-gis
=========================

|Build Status| |Coverage Status| |Code Health| |Requirements Status| |PyPI version| |PyPI downloads|

Geographic add-ons for Django Rest Framework - `Mailing
List <http://bit.ly/1M4sLTp>`__.

Install last stable version from pypi
-------------------------------------

.. code-block:: bash

    pip install djangorestframework-gis

Install development version
---------------------------

.. code-block:: bash

    pip install https://github.com/djangonauts/django-rest-framework-gis/tarball/master

Compatibility with DRF, Django and Python
-----------------------------------------

===============  ============================ ==================== ==================
DRF-gis version  DRF version                  Django version       Python version
**0.8.2**        **3.0.4** to **3.1.1**       **1.5.x** to **1.8** **2.6** to **3.4**
**0.8.1**        **3.0.4** to **3.1.1**       **1.5.x** to **1.8** **2.6** to **3.4**
**0.8**          **3.0.4**                    **1.5.x** to **1.7** **2.6** to **3.4**
**0.7**          **2.4.3**                    **1.5.x** to **1.7** **2.6** to **3.4**
**0.6**          **2.4.3**                    **1.5.x** to **1.7** **2.6** to **3.4**
**0.5**          from **2.3.14** to **2.4.2** **1.5.x** to **1.7** **2.6** to **3.4**
**0.4**          from **2.3.14** to **2.4.2** **1.5.x** to **1.7** **2.6** to **3.4**
**0.3**          from **2.3.14** to **2.4.2** **1.5.x**, **1.6.x** **2.6**, **2.7**
**0.2**          from **2.2.2** to **2.3.13** **1.5.x**, **1.6.x** **2.6**, **2.7**
===============  ============================ ==================== ==================

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

In contrast, the ``GeoModelSerializer`` will output:

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

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

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

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

    class LocationSerializer(GeoFeatureModelSerializer):

        class Meta:
            model = Location
            geo_field = "point"
            id_field = False
            fields = ('id', 'address', 'city', 'state')

You could also set the **``id_field``** to some other unique field in
your model, like **"slug"**:

.. code-block:: python

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

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

InBBoxFilter
~~~~~~~~~~~~

Provides a ``InBBoxFilter``, which is a subclass of DRF
``BaseFilterBackend``. Filters a queryset to only those instances within
a certain bounding box.


``views.py:``

.. code-block:: python

    from rest_framework_gis.filters import InBBoxFilter

    class LocationList(ListAPIView):

        queryset = models.Location.objects.all()
        serializer_class = serializers.LocationSerializer
        bbox_filter_field = 'point'
        filter_backends = (InBBoxFilter, )
        bbox_filter_include_overlapping = True # Optional

We can then filter in the URL, using Bounding Box format (min Lon, min
Lat, max Lon, max Lat), and we can search for instances within the
bounding box, e.g.:
``/location/?in_bbox=-90,29,-89,35``.

By default, InBBoxFilter will only return those instances entirely
within the stated bounding box. To include those instances which overlap
the bounding box, include ``bbox_filter_include_overlapping = True``
in your view.

Note that if you are using other filters, you'll want to include your
other filter backend in your view. For example:

``filter_backends = (InBBoxFilter, DjangoFilterBackend,)``

TMSTileFilter
~~~~~~~~~~~~~

Provides a ``TMSTileFilter``, which is a subclass of ``InBBoxFilter``.
Filters a queryset to only those instances within a bounding box defined
by a `TMS tile <http://wiki.openstreetmap.org/wiki/TMS>`__ address.

``views.py:``

.. code-block:: python

    from rest_framework_gis.filters import TMSTileFilter

    class LocationList(ListAPIView):

        queryset = models.Location.objects.all()
        serializer_class = serializers.LocationSerializer
        bbox_filter_field = 'point'
        filter_backends = (TMSTileFilter, )
        bbox_filter_include_overlapping = True # Optional

We can then filter in the URL, using TMS tile addresses in the zoom/x/y format,
eg:.
``/location/?tile=8/100/200``
which is equivalant to filtering on the bbox  (-39.37500,-71.07406,-37.96875,-70.61261).

For more information on configuration options see InBBoxFilter.

Note that the tile address start in the upper left, not the lower left origin used by some
implementations.

DistanceToPointFilter
~~~~~~~~~~~~~~~~~~~~~

Provides a ``DistanceToPointFilter``, which is a subclass of DRF
``BaseFilterBackend``. Filters a queryset to only those instances within
a certain distance of a given point.

``views.py:``

.. code-block:: python

    from rest_framework_gis.filters import DistanceToPointFilter

    class LocationList(ListAPIView):

        queryset = models.Location.objects.all()
        serializer_class = serializers.LocationSerializer
        distance_filter_field = 'geometry'
        filter_backends = (DistanceToPointFilter, )
        bbox_filter_include_overlapping = True # Optional

We can then filter in the URL, using a distance and a point in (lon, lat) format. The
distance can be given in meters or in degrees.

eg:.
``/location/?dist=4000&point=-122.4862,37.7694&format=json``
which is equivalant to filtering within 4000 meters of the point  (-122.4862, 37.7694).

By default, DistanceToPointFilter will pass the 'distance' in the URL directly to the database for the search.
The effect depends on the srid of the database in use. If geo data is indexed in meters (srid 3875, aka 900913), a
distance in meters can be passed in directly without conversion. For lat-lon databases such as srid 4326,
which is indexed in degrees, the 'distance' will be interpreted as degrees. Set the flag, 'distance_filter_convert_meters'
to 'True' in order to convert an input distance in meters to degrees. This conversion is approximate, and the errors
at latitudes > 60 degrees are > 25%.

Projects using this package
---------------------------

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
.. |Requirements Status| image:: https://requires.io/github/djangonauts/django-rest-framework-gis/requirements.png?branch=master
   :target: https://requires.io/github/djangonauts/django-rest-framework-gis/requirements/?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/djangorestframework-gis.png
   :target: http://badge.fury.io/py/djangorestframework-gis
.. |PyPI downloads| image:: https://pypip.in/d/djangorestframework-gis/badge.png
    :target: http://badge.fury.io/py/djangorestframework-gis
