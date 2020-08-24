#!/usr/bin/env python
# -------------------------------------------------------
# Translates between lat/long and the slippy-map tile
# numbering scheme
#
# http://wiki.openstreetmap.org/index.php/Slippy_map_tilenames
#
# Written by Oliver White, 2007
# This file is public-domain
# -------------------------------------------------------
from math import atan, degrees, pi
from math import pow as math_pow
from math import sinh


def num_tiles(z):
    return math_pow(2, z)


def lat_edges(y, z):
    n = num_tiles(z)
    unit = 1 / n
    relY1 = y * unit
    relY2 = relY1 + unit
    lat1 = mercator_to_lat(pi * (1 - 2 * relY1))
    lat2 = mercator_to_lat(pi * (1 - 2 * relY2))
    return (lat1, lat2)


def lon_edges(x, z):
    n = num_tiles(z)
    unit = 360 / n
    lon1 = -180 + x * unit
    lon2 = lon1 + unit
    return (lon1, lon2)


def tile_edges(x, y, z):
    lat1, lat2 = lat_edges(y, z)
    lon1, lon2 = lon_edges(x, z)
    return (lon1, lat2, lon2, lat1)  # w, s, e, n


def mercator_to_lat(mercatorY):
    return degrees(atan(sinh(mercatorY)))
