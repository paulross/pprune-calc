"""
General calculation functions for video analysis.
"""
import bisect
import math
import re
import typing


def m_p_s_to_knots(v: float) -> float:
    """Convert m/s to knots."""
    return 3600.0 * v / 0.3048 / 6080


def knots_to_m_p_s(v: float) -> float:
    """Convert knots to m/s."""
    return v * 6080 * 0.3048 / 3600


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


def google_earth_url_to_lat_long(note_url: str) -> typing.Tuple[str, float, float]:
    """
    Converts: Tower 1: https://www.google.com/maps/@-23.0039523,-47.1506005,59m/data=!3m1!1e3?hl=en
    To: ('Tower 1', -23.0039523, -47.1506005)
    """
    m = RE_GOOGLE_EARTH_URL.match(note_url)
    if m is not None:
        return (m.group(1), float(m.group(2)), float(m.group(3)))


def haversine(angle: float) -> float:
    return math.sin(math.radians(angle) / 2.0)**2


# Equatorial radius
EARTH_RADIUS_M = 6378.137e3


def distance_lat_long(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in metres between two lat/long positions.
    Lat/long in degrees."""
    t = haversine(lat2 - lat1) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * haversine(lon2 - lon1)
    d = 2 * EARTH_RADIUS_M * math.asin(math.sqrt(t))
    return d


def bearing_lat_long(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Bearing in degrees between two lat/long positons.
    Lat/long in degrees.
    https://en.wikipedia.org/wiki/Great-circle_navigation"""
    y = math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon1))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2))
    x -= math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(lon2 - lon1))
    bearing = math.atan2(y, x)
    return math.degrees(bearing) % 360


def lat_long_bearing_distance_to_lat_long(lat: float, lon: float, dist: float, brng: float) -> typing.Tuple[float, float]:
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
    dlon = a * math.sin(math.degrees(brng)) / math.cos(math.radians(lat) + dlat / 2.0)
    return lat + math.degrees(dlat), lon + math.degrees(dlon)


def lat_long_to_xy(latx: float, lonx: float,
                   bearing_x_axis: float,
                   lat: float, lon: float) -> typing.Tuple[float, float]:
    """Given datum lat/long position and bearing of the X axis this returns the x/y
    position of a lat/long position.
    Lat/long/bearing in degrees. x/y is in metres."""
    angle = bearing_lat_long(latx, lonx, lat, lon) - bearing_x_axis
    radius = distance_lat_long(latx, lonx, lat, lon)
    # print(
    #     'TRACE: bearing={:8.3f} angle={:8.3f}, radius={:8.3f}'.format(
    #         bearing_lat_long(latx, lonx, lat, lon), angle, radius
    #     )
    # )
    x = radius * math.cos(math.radians(angle))
    y = radius * math.sin(math.radians(angle))
    return x, y


def xy_to_lat_long(latx: float, lonx: float,
                   bearing_x_axis: float,
                   x: float, y: float) -> typing.Tuple[float, float]:
    """
    Given datum lat/long position and bearing of the X axis this returns the x/y
    position of a lat/long position.
    Lat/long/bearing in degrees. x/y is in metres.
    """
    angle = math.atan2(y, x) + bearing_x_axis
    radius = math.sqrt(x**2 + y**2)
    lat, lon = lat_long_bearing_distance_to_lat_long(latx, lonx, radius, angle)
    return lat, lon


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
    the distance p -> o on the transit line."""
    d = math.sqrt((oy - py)**2 + (ox - px)**2)
    return d


def transit_distance_to_x(px: float, py: float, ox: float, oy: float) -> float:
    """Given an object at position px, py and an observer as ox, oy this returns the
    the distance p -> x axis on the transit line."""
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
