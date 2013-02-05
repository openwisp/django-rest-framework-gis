# rest_framework_gis/parsers.py
import json

from rest_framework.parsers import BaseParser

class GeoJSONParser(BaseParser):
    """
    Parses GeoJSON-serialized data.
    """

    media_type = 'application/geo-json'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Returns a 2-tuple of `(data, files)`.

        `data` will be an object which is the parsed content of the response.
        `files` will always be `None`.
        """
        try:
            return json.load(stream)
        except ValueError, exc:
            raise ParseError('JSON parse error - %s' % unicode(exc))