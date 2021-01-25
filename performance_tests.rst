Average of 5 measurements for python2 and python3.

Launch the performance test with::

    cd tests
    ./manage.py test --keepdb django_restframework_gis_tests.test_performance

For more information regarding how the measurement is performed read the code in
`test_performance.py <https://github.com/openwisp/django-rest-framework-gis/blob/master/tests/django_restframework_gis_tests/test_performance.py>`__.

0.9.2
=====

- **py2**: 6.304474401472
- **py3**: 6.952443096001661

0.9.3
=====

- **py2**: 4.462462759018 (**29.2%** improvement)
- **py3**: 5.217188624000118 (**25%** improvement)

0.9.4
=====

- **py2**: 4.227859210966
- **py3**: 5.00467809599977

0.9.5
=====

- **py2**: 4.193417596816
- **py3**: 4.89978777600045
