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


def distance_bearing(a: Point, b: Point, scale: float) -> typing.Tuple[float, float]:
    """Returns distance in metres and angle in degrees between two points at a scale in m / pixel."""
    x_north = a.y - b.y
    y_east = b.x - a.x
    distance = scale * math.sqrt(x_north**2 + y_east**2)
    bearing = math.atan2(y_east, x_north)
    bearing_degrees = math.degrees(bearing)
    if bearing_degrees < 0:
        bearing_degrees += 360
    return distance, bearing_degrees


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


FRAME_RATE = 30.0


def frame_to_time(frame: typing.Union[int, float]) -> float:
    return (frame - 1) / FRAME_RATE


def frames_to_dtime(frame_a: typing.Union[int, float], frame_b: typing.Union[int, float]) -> float:
    return (frame_b - frame_a) / FRAME_RATE


def time_to_frame(time: typing.Union[int, float]) -> int:
    return 1 + int(0.5 + time * FRAME_RATE)


def distance_tolerance(distance: float) -> float:
    """Returns the error estimate of distance.
    At +2500m to the threshold this is assumed to be 100m decreasing linearly to 10m at the threshold and thereafter."""
    ret = 10.0
    if distance < 0:
        ret += distance * (100 - ret) / -2500.0
    return ret
