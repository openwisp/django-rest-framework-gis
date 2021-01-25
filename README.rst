django-rest-framework-gis
=========================

|Build Status| |Coverage Status| |Requirements Status| |PyPI version| |PyPI downloads| |Black|

Geographic add-ons for Django Rest Framework - `Mailing
List <http://bit.ly/1M4sLTp>`__.

Install last stable version from pypi
-------------------------------------

.. code-block:: bash

    pip install djangorestframework-gis

Install development version
---------------------------

.. code-block:: bash

    pip install https://github.com/openwisp/django-rest-framework-gis/tarball/master

Setup
-----

Add ``rest_framework_gis`` in ``settings.INSTALLED_APPS``, after ``rest_framework``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'rest_framework',
        'rest_framework_gis',
        # ...
    ]

Compatibility with DRF, Django and Python
-----------------------------------------

===============  ============================ ==================== ==================================
DRF-gis version  DRF version                  Django version       Python version
**0.17.x**       **3.10** up to **3.12**      **2.2 to 3.1**       **3.6** to **3.8**
**0.16.x**       **3.10**                     **2.2 to 3.1**       **3.6** to **3.8**
**0.15.x**       **3.10**                     **1.11, 2.2 to 3.0** **3.5** to **3.8**
**0.14.x**       **3.3** to **3.9**           **1.11** to **2.1**   **3.4** to **3.7**
**0.13.x**       **3.3** to **3.8**           **1.11** to **2.0**   **2.7** to **3.6**
**0.12.x**       **3.1** to **3.7**           **1.11** to **2.0**   **2.7** to **3.6**
**0.11.x**       **3.1** to **3.6**           **1.7** to **1.11**  **2.7** to **3.6**
**0.10.x**       **3.1** to **3.3**           **1.7** to **1.9**   **2.7** to **3.5**
**0.9.6**        **3.1** to **3.2**           **1.5** to **1.8**   **2.6** to **3.5**
**0.9.5**        **3.1** to **3.2**           **1.5** to **1.8**   **2.6** to **3.4**
**0.9.4**        **3.1** to **3.2**           **1.5** to **1.8**   **2.6** to **3.4**
**0.9.3**        **3.1**                      **1.5** to **1.8**   **2.6** to **3.4**
**0.9.2**        **3.1**                      **1.5** to **1.8**   **2.6** to **3.4**
**0.9.1**        **3.1**                      **1.5** to **1.8**   **2.6** to **3.4**
**0.9**          **3.1**                      **1.5** to **1.8**   **2.6**, **2.7**, **3.3**, **3.4**
**0.9**          **3.1**                      **1.5** to **1.8**   **2.6**, **2.7**, **3.3**, **3.4**
**0.9**          **3.1**                      **1.5** to **1.8**   **2.6**, **2.7**, **3.3**, **3.4**
**0.8.2**        **3.0.4** to **3.1.1**       **1.5** to **1.8**   **2.6**, **2.7**, **3.3**, **3.4**
**0.8.1**        **3.0.4** to **3.1.1**       **1.5** to **1.8**   **2.6**, **2.7**, **3.3**, **3.4**
**0.8**          **3.0.4**                    **1.5** to **1.7**   **2.6**, **2.7**, **3.3**, **3.4**
**0.7**          **2.4.3**                    **1.5** to **1.7**   **2.6**, **2.7**, **3.3**, **3.4**
**0.6**          **2.4.3**                    **1.5** to **1.7**   **2.6**, **2.7**, **3.3**, **3.4**
**0.5**          from **2.3.14** to **2.4.2** **1.5** to **1.7**   **2.6**, **2.7**, **3.3**, **3.4**
**0.4**          from **2.3.14** to **2.4.2** **1.5** to **1.7**   **2.6**, **2.7**, **3.3**, **3.4**
**0.3**          from **2.3.14** to **2.4.2** **1.5**, **1.6**     **2.6**, **2.7**
**0.2**          from **2.2.2** to **2.3.13** **1.5**, **1.6**     **2.6**, **2.7**
===============  ============================ ==================== ==================================

Fields
------

GeometryField
~~~~~~~~~~~~~

Provides a ``GeometryField``, which is a subclass of Django Rest Framework
(from now on **DRF**) ``WritableField``. This field handles GeoDjango
geometry fields, providing custom ``to_native`` and ``from_native``
methods for GeoJSON input/output.

This field takes two optional arguments:

``precision``: Passes coordinates through Python's builtin ``round()`` function (`docs
<https://docs.python.org/3/library/functions.html#round>`_), rounding values to
the provided level of precision. E.g. A Point with lat/lng of
``[51.0486, -114.0708]`` passed through a ``GeometryField(precision=2)``
would return a Point with a lat/lng of ``[51.05, -114.07]``.

``remove_duplicates``: Remove sequential duplicate coordinates from line and
polygon geometries. This is particularly useful when used with the ``precision``
argument, as the likelihood of duplicate coordinates increase as precision of
coordinates are reduced.

**Note:** While both above arguments are designed to reduce the
byte size of the API response, they will also increase the processing time
required to render the response. This will likely be negligible for small GeoJSON
responses but may become an issue for large responses.

**New in 0.9.3:** there is no need to define this field explicitly in your serializer,
it's mapped automatically during initialization in ``rest_framework_gis.apps.AppConfig.ready()``.

GeometrySerializerMethodField
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a ``GeometrySerializerMethodField``, which is a subclass of DRF
``SerializerMethodField`` and handles values which are computed with a serializer
method and are used as a ``geo_field``. `See example below <https://github.com/openwisp/django-rest-framework-gis#using-geometryserializermethodfield-as-geo_field>`__.

Serializers
-----------

GeoModelSerializer (DEPRECATED)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Deprecated, will be removed in 1.0**: Using this serializer is not needed anymore since 0.9.3, if you add
``rest_framework_gis`` in ``settings.INSTALLED_APPS`` the serialization will work out of the box with DRF.
Refer `Issue #156 <https://github.com/openwisp/django-rest-framework-gis#using-geometryserializermethodfield-as-geo_field>`__.

Provides a ``GeoModelSerializer``, which is a subclass of DRF
``ModelSerializer``. This serializer updates the field\_mapping
dictionary to include field mapping of GeoDjango geometry fields to the
above ``GeometryField``.

For example, the following model:

.. code-block:: python

    class Location(models.Model):
        """
        A model which holds information about a particular location
        """
        address = models.CharField(max_length=255)
        city = models.CharField(max_length=100)
        state = models.CharField(max_length=100)
        point = models.PointField()

By default, the DRF ModelSerializer **ver < 0.9.3** will output:

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

**Note:** For ``ver>=0.9.3``: The DRF model serializer will give the same output as above, if;

-  ``rest_framework_gis`` is set in ``settings.INSTALLED_APPS`` or
-  the field in the serializer is set explicitly as ``GeometryField``.

GeoFeatureModelSerializer
~~~~~~~~~~~~~~~~~~~~~~~~~

``GeoFeatureModelSerializer`` is a subclass of ``rest_framework.ModelSerializer``
which will output data in a format that is **GeoJSON** compatible. Using
the above example, the ``GeoFeatureModelSerializer`` will output:

.. code-block:: javascript

     {
        "id": 1,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464],
        },
        "properties": {
            "address": "742 Evergreen Terrace",
            "city":  "Springfield",
            "state": "Oregon"
        }
    }

If you are serializing an object list, ``GeoFeatureModelSerializer``
will create a ``FeatureCollection``:

.. code-block:: javascript

    {
        "type": "FeatureCollection",
        "features": [
        {
            "id": 1
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-123.0208, 44.0464],
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
                "type": "Point",
                "coordinates": [-123.0208, 44.0489],
            },
            "properties": {
                "address": "744 Evergreen Terrace",
                "city":  "Springfield",
                "state": "Oregon"
            }
        }
    }

Specifying the geometry field: "geo_field"
##########################################

``GeoFeatureModelSerializer`` requires you to define a ``geo_field``
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

Using GeometrySerializerMethodField as "geo_field"
##################################################

``geo_field`` may also be an instance of ``GeometrySerializerMethodField``.
In this case you can compute its value during serialization. For example:

.. code-block:: python

    from django.contrib.gis.geos import Point
    from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField

    class LocationSerializer(GeoFeatureModelSerializer):
        """ A class to serialize locations as GeoJSON compatible data """

        # a field which contains a geometry value and can be used as geo_field
        other_point = GeometrySerializerMethodField()

        def get_other_point(self, obj):
            return Point(obj.point.lat / 2, obj.point.lon / 2)

        class Meta:
            model = Location
            geo_field = 'other_point'

Serializer for ``geo_field`` may also return ``None`` value, which will translate to ``null`` value for geojson ``geometry`` field.

Specifying the ID: "id_field"
#############################

The primary key of the model (usually the "id" attribute) is
automatically used as the ``id`` field of each
`GeoJSON Feature Object <https://tools.ietf.org/html/draft-butler-geojson#section-2.2>`_.

The default behaviour follows the `GeoJSON RFC <https://tools.ietf.org/html/draft-butler-geojson>`_,
but it can be disabled by setting ``id_field`` to ``False``:

.. code-block:: python

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

    class LocationSerializer(GeoFeatureModelSerializer):

        class Meta:
            model = Location
            geo_field = "point"
            id_field = False
            fields = ('id', 'address', 'city', 'state')

The ``id_field`` can also be set to use some other unique field in your model, eg: ``slug``:

.. code-block:: python

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

    class LocationSerializer(GeoFeatureModelSerializer):

        class Meta:
            model = Location
            geo_field = 'point'
            id_field = 'slug'
            fields = ('slug', 'address', 'city', 'state')

Bounding Box: "auto_bbox" and "bbox_geo_field"
##############################################

The GeoJSON specification allows a feature to contain a
`boundingbox of a feature <http://geojson.org/geojson-spec.html#geojson-objects>`__.
``GeoFeatureModelSerializer`` allows two different ways to fill this property. The first
is using the ``geo_field`` to calculate the bounding box of a feature. This only allows
read access for a REST client and can be achieved using ``auto_bbox``. Example:

.. code-block:: python

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

    class LocationSerializer(GeoFeatureModelSerializer):
        class Meta:
            model = Location
            geo_field = 'geometry'
            auto_bbox = True


The second approach uses the ``bbox_geo_field`` to specify an additional
``GeometryField`` of the model which will be used to calculate the bounding box. This allows
boundingboxes differ from the exact extent of a features geometry. Additionally this
enables read and write access for the REST client. Bounding boxes send from the client will
be saved as Polygons. Example:

.. code-block:: python

    from rest_framework_gis.serializers import GeoFeatureModelSerializer

    class LocationSerializer(GeoFeatureModelSerializer):

        class Meta:
            model = BoxedLocation
            geo_field = 'geometry'
            bbox_geo_field = 'bbox_geometry'


Custom GeoJSON properties source
################################

In GeoJSON each feature can have a ``properties`` member containing the
attributes of the feature. By default this field is filled with the
attributes from your Django model, excluding the id, geometry and bounding
box fields. It's possible to override this behaviour and implement a custom
source for the ``properties`` member.

The following example shows how to use a PostgreSQL HStore field as a source for
the ``properties`` member:

.. code-block:: python

    # models.py
    class Link(models.Model):
        """
        Metadata is stored in a PostgreSQL HStore field, which allows us to
        store arbitrary key-value pairs with a link record.
        """
        metadata = HStoreField(blank=True, null=True, default=dict)
        geo = models.LineStringField()
        objects = models.GeoManager()

    # serializers.py
    class NetworkGeoSerializer(GeoFeatureModelSerializer):
        class Meta:
            model = models.Link
            geo_field = 'geo'
            auto_bbox = True

        def get_properties(self, instance, fields):
            # This is a PostgreSQL HStore field, which django maps to a dict
            return instance.metadata

        def unformat_geojson(self, feature):
            attrs = {
                self.Meta.geo_field: feature["geometry"],
                "metadata": feature["properties"]
            }

            if self.Meta.bbox_geo_field and "bbox" in feature:
                attrs[self.Meta.bbox_geo_field] = Polygon.from_bbox(feature["bbox"])

            return attrs

When the serializer renders GeoJSON, it calls the method
``get_properties`` for each object in the database. This function
should return a dictionary containing the attributes for the feature. In the
case of a HStore field, this function is easily implemented.

The reverse is also required: mapping a GeoJSON formatted structure to
attributes of your model. This task is done by ``unformat_geojson``. It should
return a dictionary with your model attributes as keys, and the corresponding
values retrieved from the GeoJSON feature data.

Pagination
----------

We provide a ``GeoJsonPagination`` class.

GeoJsonPagination
~~~~~~~~~~~~~~~~~

Based on ``rest_framework.pagination.PageNumberPagination``.

Code example:

.. code-block:: python

    from rest_framework_gis.pagination import GeoJsonPagination
    # --- other omitted imports --- #

    class GeojsonLocationList(generics.ListCreateAPIView):
        # -- other omitted view attributes --- #
        pagination_class = GeoJsonPagination

Example result response (cut to one element only instead of 10):

.. code-block:: javascript

    {
        "type": "FeatureCollection",
        "count": 25,
        "next": "http://localhost:8000/geojson/?page=2",
        "previous": null,
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        42.0,
                        50.0
                    ]
                },
                "properties": {
                    "name": "test"
                }
            }
        ]
    }


Filters
-------

**note**: this feature has been tested up to django-filter 1.0.

We provide a ``GeometryFilter`` field as well as a ``GeoFilterSet``
for usage with ``django_filter``. You simply provide, in the query
string, one of the textual types supported by ``GEOSGeometry``. By
default, this includes WKT, HEXEWKB, WKB (in a buffer), and GeoJSON.

GeometryFilter
~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework_gis.filterset import GeoFilterSet
    from rest_framework_gis.filters import GeometryFilter
    from django_filters import filters

    class RegionFilter(GeoFilterSet):
        slug = filters.CharFilter(name='slug', lookup_expr='istartswith')
        contains_geom = GeometryFilter(name='geom', lookup_expr='contains')

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
        filter_backends = (InBBoxFilter,)
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
        filter_backends = (TMSTileFilter,)
        bbox_filter_include_overlapping = True # Optional

We can then filter in the URL, using TMS tile addresses in the zoom/x/y format,
eg:.
``/location/?tile=8/100/200``
which is equivalent to filtering on the bbox  (-39.37500,-71.07406,-37.96875,-70.61261).

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
        filter_backends = (DistanceToPointFilter,)

We can then filter in the URL, using a distance and a point in (lon, lat) format. The
distance can be given in meters or in degrees.

eg:.
``/location/?dist=4000&point=-122.4862,37.7694&format=json``
which is equivalent to filtering within 4000 meters of the point  (-122.4862, 37.7694).

By default, DistanceToPointFilter will pass the 'distance' in the URL directly to the database for the search.
The effect depends on the srid of the database in use. If geo data is indexed in meters (srid 3875, aka 900913), a
distance in meters can be passed in directly without conversion. For lat-lon databases such as srid 4326,
which is indexed in degrees, the 'distance' will be interpreted as degrees. Set the flag, 'distance_filter_convert_meters'
to 'True' in order to convert an input distance in meters to degrees. This conversion is approximate, and the errors
at latitudes > 60 degrees are > 25%.

DistanceToPointOrderingFilter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a ``DistanceToPointOrderingFilter``, **available on Django >= 3.0**, which is a subclass of ``DistanceToPointFilter``.
Orders a queryset by distance to a given point, from the nearest to the most distant point.

``views.py:``

.. code-block:: python

    from rest_framework_gis.filters import DistanceToPointOrderingFilter

    class LocationList(ListAPIView):

        queryset = models.Location.objects.all()
        serializer_class = serializers.LocationSerializer
        distance_ordering_filter_field = 'geometry'
        filter_backends = (DistanceToPointOrderingFilter,)

We can then order the results by passing a point in (lon, lat) format in the URL.

eg:.
``/location/?point=-122.4862,37.7694&format=json``
will order the results by the distance to the point (-122.4862, 37.7694).

We can also reverse the order of the results by passing ``order=desc``:
``/location/?point=-122.4862,37.7694&order=desc&format=json``

Schema Generation
-----------------

Note: Schema generation support is available only for DRF >= 3.12.

Simplest Approach would be, change ``DEFAULT_SCHEMA_CLASS`` to ``rest_framework_gis.schema.GeoFeatureAutoSchema``:

.. code-block:: python

    REST_FRAMEWORK = {
        ...
        'DEFAULT_SCHEMA_CLASS': 'rest_framework_gis.schema.GeoFeatureAutoSchema',
        ...
    }

If you do not want to change default schema generator class:

-  You can pass this class as an argument to ``get_schema_view`` function `[Ref] <https://www.django-rest-framework.org/api-guide/schemas/#generating-a-dynamic-schema-with-schemaview>`__.
-  You can pass this class as an argument to the ``generateschema`` command `[Ref] <https://www.django-rest-framework.org/api-guide/schemas/#generating-a-static-schema-with-the-generateschema-management-command>`__.

Running the tests
-----------------

Required setup
==============

You need one of the `Spatial Database servers supported by
GeoDjango <https://docs.djangoproject.com/en/dev/ref/contrib/gis/db-api/#module-django.contrib.gis.db.backends>`__,
and create a database for the tests.

The following can be used with PostgreSQL:

.. code-block:: bash

  createdb django_restframework_gis
  psql -U postgres -d django_restframework_gis -c "CREATE EXTENSION postgis"

You might need to tweak the DB settings according to your DB
configuration. You can copy the file ``local_settings.example.py`` to
``local_settings.py`` and change the ``DATABASES`` and/or
``INSTALLED_APPS`` directives there.

This should allow you to run the tests already.

For reference, the following steps will setup a development environment for
contributing to the project:

-  create a spatial database named "django\_restframework\_gis"
-  create ``local_settings.py``, eg:
   ``cp local_settings.example.py local_settings.py``
-  tweak the ``DATABASES`` configuration directive according to your DB
   settings
-  uncomment ``INSTALLED_APPS``
-  run ``python manage.py syncdb``
-  run ``python manage.py collectstatic``
-  run ``python manage.py runserver``

Using tox
=========

The recommended way to run the tests is by using
`tox <https://tox.readthedocs.io/en/latest/>`__, which can be installed using
`pip install tox`.

You can use ``tox -l`` to list the available environments, and then e.g. use
the following to run all tests with Python 3.6 and Django 1.11:

.. code-block:: bash

    tox -e py36-django111

By default Django's test runner is used, but there is a variation of tox's
envlist to use pytest (using the ``-pytest`` suffix).

You can pass optional arguments to the test runner like this:

.. code-block:: bash

    tox -e py36-django111-pytest -- -k test_foo

Running tests manually
======================

Please refer to the ``tox.ini`` file for reference/help in case you want to run
tests manually / without tox.

To run tests in docker use

.. code-block:: bash

    docker-compose build
    docker-compose run --rm test

Running QA-checks
=================

Install the test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Reformat the code according to
`our coding style conventions with <https://openwisp.io/docs/developer/contributing.html#coding-style-conventions>`_:

.. code-block:: shell

    openwisp-qa-format

Run the QA checks by using

.. code-block:: shell

    ./run-qa-checks

In docker testing, QA checks are executed automatically.

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

.. |Build Status| image:: https://travis-ci.org/openwisp/django-rest-framework-gis.svg?branch=master
   :target: https://travis-ci.org/openwisp/django-rest-framework-gis
.. |Coverage Status| image:: https://coveralls.io/repos/openwisp/django-rest-framework-gis/badge.svg
   :target: https://coveralls.io/r/openwisp/django-rest-framework-gis
.. |Requirements Status| image:: https://requires.io/github/openwisp/django-rest-framework-gis/requirements.svg?branch=master
   :target: https://requires.io/github/openwisp/django-rest-framework-gis/requirements/?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/djangorestframework-gis.svg
   :target: http://badge.fury.io/py/djangorestframework-gis
.. |PyPI downloads| image:: https://pepy.tech/badge/djangorestframework-gis/month
   :target: https://pepy.tech/project/djangorestframework-gis
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://pypi.org/project/black/
