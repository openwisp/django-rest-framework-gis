import sys

from django.conf import settings

# this test must be run explicitly
# either by calling:
# django test --keepdb django_restframework_gis_tests.test_performance
# or by setting ``settings.TEST_PERFORMANCE`` to ``True``
if (
    'django_restframework_gis_tests.test_performance' in sys.argv
    or settings.TEST_PERFORMANCE
):
    from contexttimer import Timer
    from django.test import TestCase
    from rest_framework.renderers import JSONRenderer

    from rest_framework_gis import serializers as gis_serializers

    from .models import Location

    class TestRestFrameworkGisPerformance(TestCase):
        NUMBER_OF_LOCATIONS = 10000

        def _create_data(self):
            """ creates a bunch of gis models instances """
            locations = []
            name = 'l{0}'
            slug = 'l{0}'
            wkt = 'POINT (13.{0}125000020002 42.{0}565179379999)'
            for n in range(1, self.NUMBER_OF_LOCATIONS):
                locations.append(
                    Location(
                        name=name.format(n), slug=slug.format(n), geometry=wkt.format(n)
                    )
                )
            Location.objects.bulk_create(locations)

        def test_geojson_performance(self):
            class PerfSerializer(gis_serializers.GeoFeatureModelSerializer):
                class Meta:
                    model = Location
                    geo_field = 'geometry'
                    fields = '__all__'

            # create data
            self._create_data()
            # initialize serializer
            serializer = PerfSerializer(Location.objects.all(), many=True)
            with Timer() as t:
                JSONRenderer().render(serializer.data)
            # print results
            msg = 'GeoJSON rendering of {0} objects ' 'completed in {1}'.format(
                self.NUMBER_OF_LOCATIONS, t.elapsed
            )
            print('\n\033[95m{0}\033[0m'.format(msg))
