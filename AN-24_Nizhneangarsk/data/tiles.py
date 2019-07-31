import math
import typing

import map_funcs

TILE_FILES = { k : f'Tile_{k}.png' for k in range(1, 8) }
TILE_FILE_URLS = {
    1: 'https://www.google.com/maps/@55.8248042,109.6287012,832m/data=!3m1!1e3',
    2: 'https://www.google.com/maps/@55.8190304,109.6206697,832m/data=!3m1!1e3',
    3: 'https://www.google.com/maps/@55.8138262,109.6138347,831m/data=!3m1!1e3',
    4: 'https://www.google.com/maps/@55.8088004,109.6072157,835m/data=!3m1!1e3',
    5: 'https://www.google.com/maps/@55.8040851,109.6001154,834m/data=!3m1!1e3',
    6: 'https://www.google.com/maps/@55.798493,109.5920735,830m/data=!3m1!1e3',
    7: 'https://www.google.com/maps/@55.7943906,109.5867373,827m/data=!3m1!1e3',
}
TILE_WIDTH = 2560
TILE_HEIGHT = 1440
TILE_SCALE_M_PER_PIXEL = 50.0 / (2536 - 2455)
TILE_TIE_POINTS = {
    # Brown pixel on SE edge of red roofed house.
    (1, 2): (map_funcs.Point(141, 1217), map_funcs.Point(952, 179)),
    # SE point of jetty (?)
    (2, 3): (map_funcs.Point(532, 1171), map_funcs.Point(1220, 239)),
    # Centre of white mark
    (3, 4): (map_funcs.Point(1189, 1212), map_funcs.Point(1854, 312)),
    # NW tip of threshold i.e. RHS on approach
    (4, 5): (map_funcs.Point(856, 1034), map_funcs.Point(1577, 182)),
    # NE tip of threshold i.e. LHS on approach
    # # These might be a few pixels to the south east because of glare.
    # (4, 5): (map_funcs.Point(907, 1074), map_funcs.Point(1627, 222)),
    # South tip of pin identifying airport
    (5, 6): (map_funcs.Point(1137, 1254), map_funcs.Point(1952, 245)),
    # South tip of pin identifying supermarket
    (6, 7): (map_funcs.Point(1120, 1118), map_funcs.Point(1663, 375)),
}

def init_tile_offsets():
    tile_offsets = {}
    # These are the common points on both tiles
    for k, (p_i, p_j) in TILE_TIE_POINTS.items():
        dx = p_i.x - p_j.x
        dy = p_i.y - p_j.y
        tile_offsets[k] = map_funcs.Distance(dx, dy)
    return tile_offsets


TILE_OFFSETS = init_tile_offsets()


RUNWAY_22_THRESHOLD_TILE_5 = map_funcs.Point(1597, 197)
RUNWAY_22_END_TILE_6 = map_funcs.Point((736 + 774) / 2, (1276 + 1306) / 2)
RUNWAY_22_END_TILE_7 = map_funcs.Point((1279 + 1319) / 2, (532 + 564) / 2)
THRESHOLD_ON_EACH_TILE: typing.Dict[int, map_funcs.Point] = {
    k: map_funcs.point_tile_to_tile(5, RUNWAY_22_THRESHOLD_TILE_5, k, TILE_OFFSETS) for k in TILE_FILES.keys()
}
RUNWAY_WIDTH_PX = math.sqrt((1431 - 1473)**2 + (338 - 371)**2)
RUNWAY_LENGTH_HEADING = map_funcs.distance_bearing(
    RUNWAY_22_THRESHOLD_TILE_5,
    map_funcs.point_tile_to_tile(7, RUNWAY_22_END_TILE_7, 5, TILE_OFFSETS),
    TILE_SCALE_M_PER_PIXEL,
)



# Measured by drawing in the runway centreline
# Measured as the average of two points


# From a clear line across the runway on Tile 7


RUNWAY_LENGTH_HEADING = map_funcs.distance_bearing(
    RUNWAY_22_THRESHOLD_TILE_5,
    map_funcs.point_tile_to_tile(6, RUNWAY_22_END_TILE_6, 5, TILE_OFFSETS),
    TILE_SCALE_M_PER_PIXEL,
)


TILE_EXTENDED_RUNWAY_LINE = {
    k: map_funcs.tile_extended_centreline_crossing_points(
        k, RUNWAY_LENGTH_HEADING[1], THRESHOLD_ON_EACH_TILE,
        map_funcs.Distance(TILE_WIDTH, TILE_HEIGHT)) for k in TILE_FILES.keys()
}


# {frame_number : (tile, position), ...}


# After the aircraft departs the runway we have no data. There are some events though.
BOUNDARY_FENCE_TILE_7 = map_funcs.Point(988, 713)
FINAL_BUILDING_TILE_7 = map_funcs.Point(934, 743)
BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M = TILE_SCALE_M_PER_PIXEL * math.sqrt(
    (THRESHOLD_ON_EACH_TILE[7].x - BOUNDARY_FENCE_TILE_7.x) ** 2
    + (THRESHOLD_ON_EACH_TILE[7].y - BOUNDARY_FENCE_TILE_7.y) ** 2
)
FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M = TILE_SCALE_M_PER_PIXEL * math.sqrt(
    (THRESHOLD_ON_EACH_TILE[7].x - FINAL_BUILDING_TILE_7.x) ** 2
    + (THRESHOLD_ON_EACH_TILE[7].y - FINAL_BUILDING_TILE_7.y) ** 2
)
