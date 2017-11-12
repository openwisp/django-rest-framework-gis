Changelog
=========

Version 0.12.0 [2017-11-12]
---------------------------

- `#138 <https://github.com/djangonauts/django-rest-framework-gis/pull/138>`_:
  added support for ``GeometryCollection`` fields
- `#146 <https://github.com/djangonauts/django-rest-framework-gis/pull/146>`_:
  added compatibility with django-rest-framework 3.7
- `#147 <https://github.com/djangonauts/django-rest-framework-gis/pull/147>`_:
  added support to django 2.0 beta
- dropped support for django 1.7, 1.8, 1.9 and 1.10

Version 0.11.2 [2017-05-22]
---------------------------

- `eb54fc0 <https://github.com/djangonauts/django-rest-framework-gis/commit/eb54fc0>`_: ``GeometryFilter`` now use ``BaseGeometryWidget``
- `33a6418 <https://github.com/djangonauts/django-rest-framework-gis/commit/33a6418>`_: fixed tests for Django 1.11: ``Point`` comparison uses ``srid``

Version 0.11.1 [2017-05-05]
---------------------------

- `#119 <https://github.com/djangonauts/django-rest-framework-gis/issues/119>`_: Added support to "__all__" fields in serializer
- `#130 <https://github.com/djangonauts/django-rest-framework-gis/pull/130>`_: Added compatibility with DRF 3.6

Version 0.11.0 [2016-11-22]
---------------------------

- `#106 <https://github.com/djangonauts/django-rest-framework-gis/pull/106>`_: dropped support for django 1.7
- `#117 <https://github.com/djangonauts/django-rest-framework-gis/pull/117>`_: added support for django-filter 0.15
- `6479949 <https://github.com/djangonauts/django-rest-framework-gis/commit/6479949>`_: fixed tests for latest DRF 3.5 version
- `35e3b87 <https://github.com/djangonauts/django-rest-framework-gis/commit/35e3b87>`_: added official support to django 1.10

Version 0.10.1 [2016-01-06]
---------------------------

- `#93 <https://github.com/djangonauts/django-rest-framework-gis/issues/93>`_ skipped a few tests if spatialite DB backend is being used
- `#95 <https://github.com/djangonauts/django-rest-framework-gis/issues/95>`_ fixed misunderstanding regarding 0.9.6 DRF compatibility in README
- `#96 <https://github.com/djangonauts/django-rest-framework-gis/issues/96>`_ added missing assets in python package source tarball

Version 0.10.0 [2015-12-07]
---------------------------

- `#87 <https://github.com/djangonauts/django-rest-framework-gis/issues/87>`_ dropped support for old django versions and python 2.6

Version 0.9.6 [2015-11-02]
--------------------------

- `#82 <https://github.com/djangonauts/django-rest-framework-gis/issues/82>`_: avoid ``KeyError`` id field not in ``fields`` (bug introduced in 0.9.5)
- `fbaf9b1 <https://github.com/djangonauts/django-rest-framework-gis/commit/fbaf9b1>`_: improved documentation for new default ``id_field`` behaviour
- `#84 <https://github.com/djangonauts/django-rest-framework-gis/pull/84>`_: switched to ``assertAlmostEqual`` in ``test_post_location_list_EWKT`` to ease testing for debian package
- `#85 <https://github.com/djangonauts/django-rest-framework-gis/pull/85>`_: fixed serialization of properties holding ``None`` values (bug introduced in 0.9.5)
- `#86 <https://github.com/djangonauts/django-rest-framework-gis/pull/86>`_: updated advertised compatibility to include **python 3.5**

Version 0.9.5 [2015-10-12]
--------------------------

- `#71 <https://github.com/djangonauts/django-rest-framework-gis/pull/71>`_: added possibility to override GeoJSON properties in ``GeoFeatureModelSerializer``
- `52e15a5 <https://github.com/djangonauts/django-rest-framework-gis/commit/52e15a5>`_: Added default ``page_size_query_param`` in ``GeoJsonPagination``

Version 0.9.4 [2015-09-08]
--------------------------

- `#68 <https://github.com/djangonauts/django-rest-framework-gis/issues/68>`_: ensure not having drf-gis in ``INSTALLED_APPS`` works anyway
- `#76 <https://github.com/djangonauts/django-rest-framework-gis/issues/76>`_: avoid pickle errors in ``GeoJsonDict``
- `#75 <https://github.com/djangonauts/django-rest-framework-gis/pull/75>`_: return ``GEOSGeometry`` instead of geojson property

Version 0.9.3 [2015-07-22]
--------------------------

- `04fd1bf <https://github.com/djangonauts/django-rest-framework-gis/commit/04fd1bf>`_: Added ``GeoJsonPagination``
- `fe47d86 <https://github.com/djangonauts/django-rest-framework-gis/commit/fe47d86>`_: Improved ``ValidationError`` message of ``GeometryField``
- `a3ddd3d <https://github.com/djangonauts/django-rest-framework-gis/commit/a3ddd3d>`_: **Improved serialization performance between 25% and 29%**
- `fb6ed36 <https://github.com/djangonauts/django-rest-framework-gis/commit/fb6ed36>`_: ``GeoModelSerializer`` deprecated because obsolete
- `#66 <https://github.com/djangonauts/django-rest-framework-gis/pull/66>`_: geometry now allows ``None`` values according to the **GeoJSON spec**
- `#67 <https://github.com/djangonauts/django-rest-framework-gis/pull/67>`_: discern ``False`` or empty string values from ``None`` in ``GeoFeatureModelSerializer``

Version 0.9.2 [2015-07-15]
--------------------------

- `#59 <https://github.com/djangonauts/django-rest-framework-gis/pull/59>`_: Added GeometrySerializerMethodField
- `3fa2354 <https://github.com/djangonauts/django-rest-framework-gis/commit/3fa2354>`_: removed broken/obsolete/untested code

Version 0.9.1 [2015-06-28]
--------------------------

- `#63 <https://github.com/djangonauts/django-rest-framework-gis/issues/63>`_: added compatibility with python 3.2 and updated compatibility table in README
- `#60 <https://github.com/djangonauts/django-rest-framework-gis/pull/60>`_: ensure GeoJSON is rendered correctly in browsable API when using python 2
- `#62 <https://github.com/djangonauts/django-rest-framework-gis/issues/62>`_: updated django-rest-framework requirement to 3.1.3

Version 0.9 [2015-05-31]
------------------------

- `#55 <https://github.com/djangonauts/django-rest-framework-gis/pull/55>`_: Fixed exception in ``DistanceToPointFilter`` in case of invalid point
- `#58 <https://github.com/djangonauts/django-rest-framework-gis/pull/58>`_: Fixed handling of ``None`` values in ``GeoFeatureModelSerializer`` to avoid problems with ``FileField`` and ``ImageField``
- `#57 <https://github.com/djangonauts/django-rest-framework-gis/pull/57>`_: Added support for GeoJSON Bounding Boxes in ``GeoFeatureModelSerializer``

Version 0.8.2 [2015-04-29]
--------------------------

- `#53 <https://github.com/djangonauts/django-rest-framework-gis/pull/53>`_: Added support for PATCH requests in ``GeoFeatureModelSerializer``

Version 0.8.1 [2015-03-25]
--------------------------

- Added compatibility with django-rest-framework 3.1.x
- Added compatibility with django 1.8 (RC1)

Version 0.8 [2015-03-03]
------------------------

- Added compatibility with django-rest-framework 3.x

Version 0.7 [2014-10-03]
------------------------

- upgraded development status classifer to Beta
- avoid empty string in textarea widget if value is None
- allow field definition in GeoFeatureModelSerializer to be list

Version 0.6 [2014-09-24]
------------------------

- Added compatibility to django-rest-framework 2.4.3

Version 0.5 [2014-09-07]
------------------------

- added TMSTileFilter
- added DistanceToPointFilter
- renamed InBBOXFilter to InBBoxFilter
- added compatibility with DRF 2.4.0

Version 0.4 [2014-08-25]
------------------------

- python3 compatibility
- improved DRF browsable API HTML widget (textarea instead of text input)

Version 0.3 [2014-07-07]
------------------------

- added compatibility with DRF 2.3.14

Version 0.2 [2014-03-18]
------------------------

- geofilter support
- README in restructured text for pypi
- updated python package info

Version 0.1 [2013-12-30]
------------------------

- first release
