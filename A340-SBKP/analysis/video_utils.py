"""
General calculation functions for video analysis.
"""
import collections
import bisect
import math
import re
import typing

import utm


class XY(collections.namedtuple('XY', 'x, y')):
    """For x/y position in any units."""
    __slots__ = ()

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.x == other.x and self.y == other.y
        return False

    def __str__(self):
        return 'class XY: x={:.1f} y={:.1f}'.format(self.x, self.y)

    def __format__(self, format_spec):
        if format_spec:
            return 'x={x:{format_spec}} y={y:{format_spec}}'.format(
                x=self.x, y=self.y, format_spec=format_spec
            )
        return 'x={:.1f} y={:.1f}'.format(self.x, self.y)


class LatLong(collections.namedtuple('LatLong', 'lat, long')):
    """Latitude and Longitude."""
    __slots__ = ()

    def __eq__(self, other) -> bool:
        if self.__class__ == other.__class__:
            return self.lat == other.lat and self.long == other.long
        return False

    def __str__(self) -> str:
        return 'lat={:.7f} long={:.7f}'.format(self.lat, self.long)

    def __format__(self, format_spec: str) -> str:
        if format_spec:
            return 'lat={lat:{format_spec}} long={long:{format_spec}}'.format(
                lat=self.lat, long=self.long, format_spec=format_spec
            )
        return 'lat={:.7f} long={:.7f}'.format(self.lat, self.long)

    def _devDMM(self, v: float) -> typing.Tuple[int, float]:
        if v >= 0:
            return int(v), 60 * (v % 1.0)
        return int(v), 60.0 - 60.0 * (v % 1.0)

    @property
    def latDMM(self) -> typing.Tuple[int, float]:
        return self._devDMM(self.lat)

    @property
    def longDMM(self) -> typing.Tuple[int, float]:
        return self._devDMM(self.long)


MPS_TO_KNOTS = 3600.0 / 0.3048 / 6080


def m_p_s_to_knots(v: float) -> float:
    """Convert m/s to knots."""
    return v * MPS_TO_KNOTS


def knots_to_m_p_s(v: float) -> float:
    """Convert knots to m/s."""
    return v / MPS_TO_KNOTS


def num_k_of_n(n: int, k: int) -> int:
    """Return number of combinations of k elements out of n."""
    if k > n:
        return 0
    if k == n:
        return 1
    return math.factorial(n) // (math.factorial(k) * math.factorial((n - k)))


def triangle_ASA(alpha: float, c: float, beta: float) -> typing.Tuple[float, float, float]:
    """Given angle at A, included side A-B, angle at B of a plane triangle
    this returns side A-C, angle at C, side C-B. Angles in radians.
    See: https://en.wikipedia.org/wiki/Solution_of_triangles#A_side_and_two_adjacent_angles_given_(ASA)
    """
    if alpha <= 0.0:
        raise ValueError('Angle alpha must be > 0.0 not {}'.format(alpha))
    if c <= 0.0:
        raise ValueError('Side c must be > 0.0 not {}'.format(c))
    if beta <= 0.0:
        raise ValueError('Angle beta must be > 0.0 not {}'.format(beta))
    gamma = math.pi - alpha - beta
    factor = c / math.sin(gamma)
    a = factor * math.sin(alpha)
    b = factor * math.sin(beta)
    return b, gamma, a


def aspect_intersection(d0: float, b0: float, d1: float, b1: float) -> typing.Tuple[float, float]:
    """Given distance d0 (metres), bearing b0 (degrees), distance d1 (metres),
    bearing b1 (degrees) this returns d, y (metres) of their intersection."""
    b0 = b0 % 360
    b1 = b1 % 360
    if d1 < d0:
        # Swap positions
        d0, d1 = d1, d0
        b0, b1 = b1, b0
    if b0 < 180:
        y_positive = True
        if b1 < b0:
            raise ValueError('Both bearings must be 0-180, not {} <-> {}'.format(b0, b1))
        beta = math.radians(b0)
        alpha = math.radians(180 - b1)
    else:
        y_positive = False
        if b1 > b0:
            raise ValueError('Both bearings must be 180-360, not {} <-> {}'.format(b0, b1))
        beta = math.radians(360 - b0)
        alpha = math.radians(b1 - 180)
    _b, _gamma, a = triangle_ASA(alpha, d1 - d0, beta)
    d = d0 + a * math.cos(beta)
    y = a * math.sin(beta)
    if y_positive:
        return d, y
    return d, -y


def interpolate(xS: typing.List[float], yS: typing.List[float], x: float) -> float:
    """Linear interpolation with extrapolation."""
    if len(xS) != len(yS):
        raise ValueError('Lengths x: {} != y: {}'.format(len(xS), len(yS)))
    i = bisect.bisect_left(xS, x)
    if i == len(xS):
        if len(xS) < 2:
            raise ValueError('Overflow, can not extrapolate')
        # Extrapolate from end
        dy_dx = (yS[-1] - yS[-2]) / (xS[-1] - xS[-2])
        return yS[-1] + dy_dx * (x - xS[-1])
    if xS[i] == x:
        return yS[i]
    if i == 0:
        if len(xS) < 2:
            raise ValueError('Underflow, can not extrapolate')
        # Extrapolate from begining
        dy_dx = (yS[1] - yS[0]) / (xS[1] - xS[0])
        return yS[0] + dy_dx * (x - xS[0])
    dx = xS[i] - xS[i-1]
    frac = (x - xS[i -1]) / dx
    dy = yS[i] - yS[i-1]
    y = yS[i-1] + frac * dy
    return y


def interpolate_between_two_points(x0: float, y0: float,
                                   x1: float, y1: float,
                                   proportion: float) -> typing.Tuple[float, float]:
    """
    Given two points and a proportion of the distance between them this return the interpolated point.
    """
    if proportion == 0:
        return x0, y0
    if proportion == 1:
        return x1, y1
    return x0 + (x1 - x0) * proportion,\
           y0 + (y1 - y0) * proportion


# def intersect_two_lines(x00: float, y00: float, x01: float, y01: float,
#                         x10: float, y10: float, x11: float, y11: float) -> typing.Tuple[float, float]:
#     """
#     Given two lines, defined by two points each this returns the intersection point.
#     """
#     dydx0 = (y01 - y00) / (x01 - x00)
#     dydx1 = (y11 - y10) / (x11 - x10)
#     x = (x00 * dydx0 - x10 * dydx1 + y10 - y00) / (dydx0 - dydx1)
#     y = (x - x00) * dydx0 + y00
#     return x, y


def intersect_two_lines(line1from: XY, line1to: XY,
                        line2from: XY, line2to: XY,) -> XY:
    """
    Given two lines, defined by two points each this returns the intersection point.
    """
    dydx1 = (line1to.y - line1from.y) / (line1to.x - line1from.x)
    dydx2 = (line2to.y - line2from.y) / (line2to.x - line2from.x)
    x = (line1from.x * dydx1 - line2from.x * dydx2 + line2from.y - line1from.y) / (dydx1 - dydx2)
    y = (x - line1from.x) * dydx1 + line1from.y
    return XY(x, y)


def polynomial_3(x, a, b, c, d):
    """Polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3"""
    return a + x * (b + x * (c + x * d))


def polynomial_3_integral_from_zero(x, a, b, c, d):
    """Integral of polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3.
    Integral(f(x)) 0 -> x = a * x + b * x**2 / 2 + c * x**3 / 3 + d * x**4 / 4
    """
    return x * (a + x * (b / 2.0 + x * (c / 3.0 + x * d / 4.0)))


def polynomial_3_integral(x0, x1, a, b, c, d):
    """Integral of polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3.
    """
    return a * (x1 - x0) \
            + b * (x1**2 - x0**2) / 2.0 \
            + c * (x1**3 - x0**3) / 3.0 \
            + d * (x1**4 - x0**4) / 4.0


def polynomial_3_differential(x, a, b, c, d):
    """Polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3
    Differential(f(x) = b + 2.0 * c * x**1 + 3.0 * d * x**2
    """
    return b + 2.0 * c * x + 3.0 * d * x**2


def polynomial_4(x, a, b, c, d, e):
    return a + x * (b + x * (c + x * (d + x * e)))


def polynomial_4_integral_from_zero(x, a, b, c, d, e):
    return x * (a + x * (b / 2.0 + x * (c / 3.0 + x * (d / 4.0 + x * e / 5.0))))


def polynomial_4_integral(x0, x1, a, b, c, d, e):
    return a * (x1 - x0) \
            + b * (x1**2 - x0**2) / 2.0 \
            + c * (x1**3 - x0**3) / 3.0 \
            + d * (x1**4 - x0**4) / 4.0 \
            + e * (x1**5 - x0**5) / 5.0


def polynomial_4_differential(x, a, b, c, d, e):
    return b + 2.0 * c * x + 3.0 * d * x**2 + 4.0 * e * x**3


RE_GOOGLE_EARTH_URL = re.compile(r'^(.+?): https://www.google.com/maps/@([-0-9.]+),([-0-9.]+).+$')


def google_earth_url_to_lat_long(note_url: str) -> typing.Tuple[str, LatLong]:
    """
    Converts: Tower 1: https://www.google.com/maps/@-23.0039523,-47.1506005,59m/data=!3m1!1e3?hl=en
    To: ('Tower 1', LatLong(-23.0039523, -47.1506005))
    """
    m = RE_GOOGLE_EARTH_URL.match(note_url)
    if m is not None:
        return m.group(1), LatLong(float(m.group(2)), float(m.group(3)))
    raise ValueError('Can not match: "{}"'.format(note_url))


def haversine(angle: float) -> float:
    return math.sin(math.radians(angle) / 2.0)**2


# Equatorial radius
# See: https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system
EARTH_RADIUS_M = 6378.137e3


def distance_lat_long(pos1: LatLong, pos2: LatLong) -> float:
    """Distance in metres between two lat/long positions.
    Lat/long in degrees."""
    # (easting, northing, zone_num, zone_letter)
    utm1 = utm.from_latlon(pos1.lat, pos1.long)
    utm2 = utm.from_latlon(pos2.lat, pos2.long)
    if utm1[2] == utm2[2]:
        # Same zone
        de = utm2[0] - utm1[0]
        dn = utm2[1] - utm1[1]
        return math.sqrt(de**2 + dn**2)
    else:
        t = haversine(pos2.lat - pos1.lat) \
            + math.cos(math.radians(pos1.lat)) * math.cos(math.radians(pos2.lat)) * haversine(pos2.long - pos1.long)
        d = 2 * EARTH_RADIUS_M * math.asin(math.sqrt(t))
        return d


def bearing_lat_long(pos1: LatLong, pos2: LatLong) -> float:
    """Bearing in degrees between two lat/long positons.
    Lat/long in degrees.
    https://en.wikipedia.org/wiki/Great-circle_navigation"""
    # (easting, northing, zone_num, zone_letter)
    utm1 = utm.from_latlon(pos1.lat, pos1.long)
    utm2 = utm.from_latlon(pos2.lat, pos2.long)
    if utm1[2] == utm2[2]:
        # Same zone
        y = utm2[0] - utm1[0]
        x = utm2[1] - utm1[1]
    else:
        y = math.cos(math.radians(pos2.lat)) * math.sin(math.radians(pos2.long - pos1.long))
        x = math.cos(math.radians(pos1.lat)) * math.sin(math.radians(pos2.lat))
        x -= math.sin(math.radians(pos1.lat)) * math.cos(math.radians(pos2.lat)) * math.cos(math.radians(pos2.long - pos1.long))
    bearing = math.atan2(y, x)
    return math.degrees(bearing) % 360


def lat_long_bearing_distance_to_lat_long(pos: LatLong, dist: float, brng: float) -> typing.Tuple[float, float]:
    """Given a lat/long and a bearing/distance this returns the new lat/long.
    We know c, a and B (i.e. two sides and included angle) and wish to
    compute A (dlong) and b (co-lat)

    https://en.wikipedia.org/wiki/Spherical_trigonometry
    """
    # c = math.radians(90 - lat)
    # a = math.pi * dist / EARTH_RADIUS_M
    # B = math.radians(brng)
    # # Cosine rule for b
    # b = math.acos(math.cos(c) * math.cos(a) + math.sin(c) * math.sin(a) * math.cos(B))
    # # Sin rule for A
    # A = math.asin(math.sin(a) * math.sin(B) / math.sin(b))
    # return 90 - math.degrees(b), lon + math.degrees(A)

    # FIXME: Failing round trip tests
    a = math.pi * dist / EARTH_RADIUS_M
    dlat = a * math.cos(math.degrees(brng))
    dlon = a * math.sin(math.degrees(brng)) / math.cos(math.radians(pos.lat) + dlat / 2.0)
    return pos.lat + math.degrees(dlat), pos.long + math.degrees(dlon)


def lat_long_to_xy(datum: LatLong,
                   bearing_x_axis: float,
                   pos: LatLong) -> XY:
    """Given datum lat/long position and bearing of the X axis this returns the x/y
    position of a lat/long position.
    Lat/long/bearing in degrees. x/y is in metres."""
    angle = bearing_lat_long(datum, pos) - bearing_x_axis
    radius = distance_lat_long(datum, pos)
    # print(
    #     'TRACE: bearing={:8.3f} angle={:8.3f}, radius={:8.3f}'.format(
    #         bearing_lat_long(latx, lonx, lat, lon), angle, radius
    #     )
    # )
    x = radius * math.cos(math.radians(angle))
    y = radius * math.sin(math.radians(angle))
    return XY(x, y)


def xy_to_lat_long(datum: LatLong,
                   bearing_x_axis: float,
                   xy: XY) -> LatLong:
    """
    Given datum lat/long position and bearing of the X axis this returns the lat/long
    position of a x/y position.
    Lat/long/bearing in degrees. x/y is in metres.
    """
    angle = math.atan2(xy.y, xy.x) + bearing_x_axis
    radius = math.sqrt(xy.x**2 + xy.y**2)
    result = lat_long_bearing_distance_to_lat_long(datum, radius, angle)
    return result


def transit_x_axis_intercept(px: float, py: float, ox: float, oy: float) -> float:
    """Given an object at position px, py and an observer as ox, oy this returns the
    value on the x axis of the transit line."""
    x = px + py * (ox - px) / (py - oy)
    return x


def transit_bearing(px: float, py: float, ox: float, oy: float) -> float:
    """Given an object at position px, py and an observer as ox, oy this returns the
    the bearing p -> o of the transit line in degrees."""
    b = math.atan2(oy - py, ox - px)
    return math.degrees(b)


def transit_distance(px: float, py: float, ox: float, oy: float) -> float:
    """Given an object at position px, py and an observer as ox, oy this returns the
    the distance p -> o."""
    d = math.sqrt((oy - py)**2 + (ox - px)**2)
    return d


def transit_distance_to_x(px: float, py: float, ox: float, oy: float) -> float:
    """Given an object at position px, py and an observer as ox, oy this returns the
    the distance p -> x axis on the line."""
    d = transit_distance(px, py, ox, oy)
    d = d * py / (py - oy)
    return d


def transit_x_axis_error(px: float, py: float, ox: float, oy: float, p_err: float, o_err: float) -> float:
    """Given an object at position px, py and an observer as ox, oy and the uncertainty of both
    positions this returns the uncertainty on the x axis."""
    d = transit_distance(px, py, ox, oy)
    d_x = transit_distance_to_x(px, py, ox, oy)
    x_err = p_err - (p_err - o_err) * d_x / d
    return x_err


def transit_line_past_observer(linefrom: XY, lineto: XY, observer: XY, extra: float) -> XY:
    """
    Given a transit line from/to positions and an observer this calculates the x, y position
    of the line extended past the observer by extra amount.
    """
    bearing = transit_bearing(linefrom.x, linefrom.y, lineto.x, lineto.y)
    distance = transit_distance(linefrom.x, linefrom.y, observer.x, observer.y) + extra
    x = distance * math.cos(math.radians(bearing))
    y = distance * math.sin(math.radians(bearing))
    return XY(linefrom.x + x, linefrom.y + y)
