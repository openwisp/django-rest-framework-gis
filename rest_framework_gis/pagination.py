from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class GeoJsonPagination(pagination.PageNumberPagination):
    """
    A geoJSON implementation of a pagination serializer.
    """
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('type', 'FeatureCollection'),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('features', data['features'])
        ]))
