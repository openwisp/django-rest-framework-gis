Changelog
=========

Version 0.17.0 [2021-01-25]
---------------------------

- [feature] Added
  `OpenAPI Schema Generation <https://github.com/openwisp/django-rest-framework-gis#schema-generation>`_
  (`#219 <https://github.com/openwisp/django-rest-framework-gis/issues/219>`_) - special
  thanks to `Dhaval Mehta <https://github.com/dhaval-mehta>`_

Version 0.16.0 [2020-09-07]
---------------------------

- [fix] Added support for representation of empty geometries
  (`#168 <https://github.com/openwisp/django-rest-framework-gis/issues/168>`_)
- [fix] Don't override the additional arguments passed as ``style`` to ``GeometryField``
- [feature] Added `DistanceToPointOrderingFilter <https://github.com/openwisp/django-rest-framework-gis#distancetopointorderingfilter>`_
  (`#210 <https://github.com/openwisp/django-rest-framework-gis/issues/210>`_)
- [deps] Added support for django 3.1 in the CI build
- [deps] Dropped django 1.11 and Python 3.5 from the CI build,
  compatibility may still work but it's not guaranteed anymore, please upgrade!
- [qa] Added QA checks to CI build
  (`#230 <https://github.com/openwisp/django-rest-framework-gis/issues/230>`_)

Version 0.15.0 [2019-12-09]
---------------------------

- Dropped Python 3.4 support
- `#190 <https://github.com/openwisp/django-rest-framework-gis/pull/190>`_:
  Added django 2.2 on test matrix
- `#199 <https://github.com/openwisp/django-rest-framework-gis/pull/199>`_:
  Dropped Django 2.0 support
- `#195 <https://github.com/openwisp/django-rest-framework-gis/pull/195>`_:
  Updated the way that ``to_representation`` removes already processed
- `#197 <https://github.com/openwisp/django-rest-framework-gis/pull/197>`_:
  Removed six dependency
- `#202 <https://github.com/openwisp/django-rest-framework-gis/pull/202>`_:
  Updated DRF to 3.10, removed support for previous DRF versions
- `#200 <https://github.com/openwisp/django-rest-framework-gis/pull/200>`_:
  Added Django 3.0 and Python 3.8 support

Version 0.14.0 [2018-12-02]
---------------------------

- `#173 <https://github.com/openwisp/django-rest-framework-gis/pull/173>`_:
  added support for django 2.1, DRF 3.9 and switched to django-filters >= 2.0
  (**which requires python >= 3.4**)
- `#178 <https://github.com/openwisp/django-rest-framework-gis/pull/178>`_:
  simplified ``setup.py`` and tox build

Version 0.13.0 [2018-04-27]
---------------------------

- `#161 <https://github.com/openwisp/django-rest-framework-gis/pull/161>`_:
  added flag to reduce precision of ``GeometryField``
- `#164 <https://github.com/openwisp/django-rest-framework-gis/pull/164>`_:
  added compatibility with django-rest-framework 3.8

Version 0.12.0 [2017-11-12]
---------------------------

- `#138 <https://github.com/openwisp/django-rest-framework-gis/pull/138>`_:
  added support for ``GeometryCollection`` fields
- `#146 <https://github.com/openwisp/django-rest-framework-gis/pull/146>`_:
  added compatibility with django-rest-framework 3.7
- `#147 <https://github.com/openwisp/django-rest-framework-gis/pull/147>`_:
  added support to django 2.0 beta
- dropped support for django 1.7, 1.8, 1.9 and 1.10

Version 0.11.2 [2017-05-22]
---------------------------

- `eb54fc0 <https://github.com/openwisp/django-rest-framework-gis/commit/eb54fc0>`_: ``GeometryFilter`` now use ``BaseGeometryWidget``
- `33a6418 <https://github.com/openwisp/django-rest-framework-gis/commit/33a6418>`_: fixed tests for Django 1.11: ``Point`` comparison uses ``srid``

Version 0.11.1 [2017-05-05]
---------------------------

- `#119 <https://github.com/openwisp/django-rest-framework-gis/issues/119>`_: Added support to "__all__" fields in serializer
- `#130 <https://github.com/openwisp/django-rest-framework-gis/pull/130>`_: Added compatibility with DRF 3.6

Version 0.11.0 [2016-11-22]
---------------------------

- `#106 <https://github.com/openwisp/django-rest-framework-gis/pull/106>`_: dropped support for django 1.7
- `#117 <https://github.com/openwisp/django-rest-framework-gis/pull/117>`_: added support for django-filter 0.15
- `6479949 <https://github.com/openwisp/django-rest-framework-gis/commit/6479949>`_: fixed tests for latest DRF 3.5 version
- `35e3b87 <https://github.com/openwisp/django-rest-framework-gis/commit/35e3b87>`_: added official support to django 1.10

Version 0.10.1 [2016-01-06]
---------------------------

- `#93 <https://github.com/openwisp/django-rest-framework-gis/issues/93>`_ skipped a few tests if spatialite DB backend is being used
- `#95 <https://github.com/openwisp/django-rest-framework-gis/issues/95>`_ fixed misunderstanding regarding 0.9.6 DRF compatibility in README
- `#96 <https://github.com/openwisp/django-rest-framework-gis/issues/96>`_ added missing assets in python package source tarball

Version 0.10.0 [2015-12-07]
---------------------------

- `#87 <https://github.com/openwisp/django-rest-framework-gis/issues/87>`_ dropped support for old django versions and python 2.6

Version 0.9.6 [2015-11-02]
--------------------------

- `#82 <https://github.com/openwisp/django-rest-framework-gis/issues/82>`_: avoid ``KeyError`` id field not in ``fields`` (bug introduced in 0.9.5)
- `fbaf9b1 <https://github.com/openwisp/django-rest-framework-gis/commit/fbaf9b1>`_: improved documentation for new default ``id_field`` behaviour
- `#84 <https://github.com/openwisp/django-rest-framework-gis/pull/84>`_: switched to ``assertAlmostEqual`` in ``test_post_location_list_EWKT`` to ease testing for debian package
- `#85 <https://github.com/openwisp/django-rest-framework-gis/pull/85>`_: fixed serialization of properties holding ``None`` values (bug introduced in 0.9.5)
- `#86 <https://github.com/openwisp/django-rest-framework-gis/pull/86>`_: updated advertised compatibility to include **python 3.5**

Version 0.9.5 [2015-10-12]
--------------------------

- `#71 <https://github.com/openwisp/django-rest-framework-gis/pull/71>`_: added possibility to override GeoJSON properties in ``GeoFeatureModelSerializer``
- `52e15a5 <https://github.com/openwisp/django-rest-framework-gis/commit/52e15a5>`_: Added default ``page_size_query_param`` in ``GeoJsonPagination``

Version 0.9.4 [2015-09-08]
--------------------------

- `#68 <https://github.com/openwisp/django-rest-framework-gis/issues/68>`_: ensure not having drf-gis in ``INSTALLED_APPS`` works anyway
- `#76 <https://github.com/openwisp/django-rest-framework-gis/issues/76>`_: avoid pickle errors in ``GeoJsonDict``
- `#75 <https://github.com/openwisp/django-rest-framework-gis/pull/75>`_: return ``GEOSGeometry`` instead of geojson property

Version 0.9.3 [2015-07-22]
--------------------------

- `04fd1bf <https://github.com/openwisp/django-rest-framework-gis/commit/04fd1bf>`_: Added ``GeoJsonPagination``
- `fe47d86 <https://github.com/openwisp/django-rest-framework-gis/commit/fe47d86>`_: Improved ``ValidationError`` message of ``GeometryField``
- `a3ddd3d <https://github.com/openwisp/django-rest-framework-gis/commit/a3ddd3d>`_: **Improved serialization performance between 25% and 29%**
- `fb6ed36 <https://github.com/openwisp/django-rest-framework-gis/commit/fb6ed36>`_: ``GeoModelSerializer`` deprecated because obsolete
- `#66 <https://github.com/openwisp/django-rest-framework-gis/pull/66>`_: geometry now allows ``None`` values according to the **GeoJSON spec**
- `#67 <https://github.com/openwisp/django-rest-framework-gis/pull/67>`_: discern ``False`` or empty string values from ``None`` in ``GeoFeatureModelSerializer``

Version 0.9.2 [2015-07-15]
--------------------------

- `#59 <https://github.com/openwisp/django-rest-framework-gis/pull/59>`_: Added GeometrySerializerMethodField
- `3fa2354 <https://github.com/openwisp/django-rest-framework-gis/commit/3fa2354>`_: removed broken/obsolete/untested code

Version 0.9.1 [2015-06-28]
--------------------------

- `#63 <https://github.com/openwisp/django-rest-framework-gis/issues/63>`_: added compatibility with python 3.2 and updated compatibility table in README
- `#60 <https://github.com/openwisp/django-rest-framework-gis/pull/60>`_: ensure GeoJSON is rendered correctly in browsable API when using python 2
- `#62 <https://github.com/openwisp/django-rest-framework-gis/issues/62>`_: updated django-rest-framework requirement to 3.1.3

Version 0.9 [2015-05-31]
------------------------

- `#55 <https://github.com/openwisp/django-rest-framework-gis/pull/55>`_: Fixed exception in ``DistanceToPointFilter`` in case of invalid point
- `#58 <https://github.com/openwisp/django-rest-framework-gis/pull/58>`_: Fixed handling of ``None`` values in ``GeoFeatureModelSerializer`` to avoid problems with ``FileField`` and ``ImageField``
- `#57 <https://github.com/openwisp/django-rest-framework-gis/pull/57>`_: Added support for GeoJSON Bounding Boxes in ``GeoFeatureModelSerializer``

Version 0.8.2 [2015-04-29]
--------------------------

- `#53 <https://github.com/openwisp/django-rest-framework-gis/pull/53>`_: Added support for PATCH requests in ``GeoFeatureModelSerializer``

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
