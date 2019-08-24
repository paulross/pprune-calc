import math
import typing


class Point(typing.NamedTuple):
    x: typing.Union[int, float]
    y: typing.Union[int, float]


class Distance(typing.NamedTuple):
    x: typing.Union[int, float]
    y: typing.Union[int, float]


def point_tile_to_tile(tile_a: int, pt_a: Point, tile_b: int,
                       tile_offsets: typing.Dict[typing.Tuple[int, int], Distance]) -> Point:
    if tile_a == tile_b:
        # Same tile
        return pt_a
    else:
        dx = dy = 0
        if tile_b > tile_a:
            while tile_a != tile_b:
                d_ab = tile_offsets[tile_a, tile_a + 1]
                dx += d_ab.x
                dy += d_ab.y
                tile_a += 1
        else:
            # tile_a > tile_b
            while tile_a != tile_b:
                d_ab = tile_offsets[tile_b, tile_b + 1]
                dx -= d_ab.x
                dy -= d_ab.y
                tile_b += 1
        ret_x = pt_a.x - dx
        ret_y = pt_a.y - dy
    return Point(ret_x, ret_y)


def distance(a: Point, b: Point, scale: float) -> float:
    """Returns distance in metres two points at a scale in m / pixel."""
    x_north = a.y - b.y
    y_east = b.x - a.x
    return scale * math.sqrt(x_north**2 + y_east**2)


def bearing(a: Point, b: Point) -> float:
    """Returns angle in degrees between two points at a scale in m / pixel."""
    x_north = a.y - b.y
    y_east = b.x - a.x
    _bearing = math.atan2(y_east, x_north)
    bearing_degrees = math.degrees(_bearing)
    if bearing_degrees < 0:
        bearing_degrees += 360
    return bearing_degrees


def bearing_min_max(a: Point, b: Point, disp: float) -> typing.Tuple[float, float]:
    d_range = (-disp, +disp)
    bearings = []
    for dx_a in d_range:
        for dy_a in d_range:
            for dx_b in d_range:
                for dy_b in d_range:
                    new_a = Point(a.x + dx_a, a.y + dy_a)
                    new_b = Point(b.x + dx_b, b.y + dy_b)
                    bearings.append(bearing(new_a, new_b))
    # print('TRACE:', bearings)
    return min(bearings), max(bearings)


def translate_rotate(pt: Point, rotation_degrees: float, origin: Point=Point(0, 0)) -> Point:
    cos = math.cos(math.radians(rotation_degrees))
    sin = math.sin(math.radians(rotation_degrees))
    ret = Point(
        (origin.y - pt.y) * cos - (origin.x - pt.x) * sin,
        -((origin.x - pt.x) * cos + (origin.y - pt.y) * sin),
    )
    return ret


def point_translate(pt: Point, bearing_degrees: float, length: float) -> Point:
    ret = Point(
        pt.x + length * math.sin(math.radians(bearing_degrees)),
        pt.y - length * math.cos(math.radians(bearing_degrees)),
    )
    return ret


def distance_bearing(a: Point, b: Point, scale: float) -> typing.Tuple[float, float]:
    """Returns distance in metres and angle in degrees between two points at a scale in m / pixel."""
    return distance(a, b, scale), bearing(a, b)


def xy_from_two_points_and_axis(a: Point, b: Point, axis_deg: float, scale: float) -> Point:
    dist_m, brg_deg = distance_bearing(a, b, scale)
    x = dist_m * math.cos(math.radians(brg_deg - axis_deg))
    y = dist_m * math.sin(math.radians(brg_deg - axis_deg))
    return Point(x, y)


def mid_point(a: Point, b: Point) -> Point:
    """The mid point between two points."""
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)


def distance_between_points(a: Point, b: Point) -> float:
    """The distance between two points."""
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)


def tile_extended_centreline_crossing_points(tile: int,
                                             runway_heading: float,
                                             threshold_on_each_tile: typing.Dict[int, Point],
                                             tiled_image_size: Distance) -> typing.Tuple[Point, Point]:
    back_bearing = runway_heading - 180
    # back_bearing += .5
    t_x, t_y = threshold_on_each_tile[tile]
    pt_y_zero = Point(
        int(0.5 + t_x + t_y * math.tan(math.radians(back_bearing))),
        0,
    )
    pt_y_max = Point(
        int(0.5 + t_x + (t_y - tiled_image_size.y) * math.tan(math.radians(back_bearing))),
        tiled_image_size.y - 1
    )
    return pt_y_zero, pt_y_max


def distance_tile_to_tile(tile_a: int, pt_a: Point, tile_b: int, pt_b: Point,
                          tile_offsets: typing.Dict[typing.Tuple[int, int], Distance]) -> Distance:
    """Given two tiles and a point on each this computes the distance between the two points in global space.

    Formulae for a point on one tile to another tile::

        dx(i, j) = x(i) - x(j)
        dy(i, j) = y(i) - y(j)
    """
    if tile_a == tile_b:
        # Same tile
        ret_x = pt_a.x
        ret_y = pt_a.y
    else:
        dx = dy = 0
        if tile_b > tile_a:
            while tile_a != tile_b:
                d_ab = tile_offsets[tile_a, tile_a + 1]
                dx += d_ab.x
                dy += d_ab.y
                tile_a += 1
        else:
            # tile_a > tile_b
            while tile_a != tile_b:
                d_ab = tile_offsets[tile_b, tile_b + 1]
                dx -= d_ab.x
                dy -= d_ab.y
                tile_b += 1
        ret_x = pt_a.x - dx
        ret_y = pt_a.y - dy
    return Distance(pt_b.x - ret_x, pt_b.y - ret_y)


def metres_per_second_to_knots(m_s: float) -> float:
    # https://en.wikipedia.org/wiki/Knot_(unit)
    return m_s * 3600 / 1852


def frame_to_time(frame: typing.Union[int, float], frame_rate: int) -> float:
    return (frame - 1) / frame_rate


def frames_to_dtime(frame_a: typing.Union[int, float], frame_b: typing.Union[int, float], frame_rate: int) -> float:
    return (frame_b - frame_a) / frame_rate


def time_to_frame(time: typing.Union[int, float], frame_rate: int) -> int:
    return 1 + int(0.5 + time * frame_rate)


def distance_tolerance(distance: float) -> float:
    """Returns the error estimate of distance.
    At +2500m to the threshold this is assumed to be 100m decreasing linearly to 10m at the threshold and thereafter."""
    ret = 10.0
    if distance < 0:
        ret += distance * (100 - ret) / -2500.0
    return ret
