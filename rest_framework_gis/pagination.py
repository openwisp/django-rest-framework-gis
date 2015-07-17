from rest_framework import pagination
from rest_framework.response import Response

from .utils import OrderedDict


class GeoJsonPagination(pagination.PageNumberPagination):
    """
    A geoJSON implementation of a pagination serializer.
    """
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('type', 'FeatureCollection'),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('features', data['features'])
        ]))
