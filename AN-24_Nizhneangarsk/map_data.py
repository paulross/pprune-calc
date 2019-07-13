"""
Discussion: https://www.pprune.org/rumours-news/622950-angara-airlines-24-landing-accident-nizhneangarsk.html

Video: https://youtu.be/LtJcgdU5MUk

Data from google maps and OpenStreetMap

Accident: https://en.wikipedia.org/wiki/Angara_Airlines_Flight_200

Nizhneangarsk Airport
---------------------
Airport location (https://en.wikipedia.org/wiki/Nizhneangarsk_Airport): 55°48′6″N 109°35′12″E
That is 55.80166666666666, 109.58666666666666

IATA: none ICAO: UIUN
Runway is 04/22, 1653m long

Threshold of 22 on google maps: https://www.google.com/maps/@55.807288,109.6034312,757m/data=!3m1!1e3

RT videos: https://www.rt.com/news/462775-russia-nizhneangarsk-crash-landing/

"""
import math
import pprint
import typing

import numpy as np

import map_funcs

#==================== New tiles ======================

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

# These are the common points on both tiles
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

TILE_OFFSETS = {}
for k, (p_i, p_j) in TILE_TIE_POINTS.items():
    dx = p_i.x - p_j.x
    dy = p_i.y - p_j.y
    TILE_OFFSETS[k] = map_funcs.Distance(dx, dy)


# Measured by drawing in the runway centreline
RUNWAY_22_THRESHOLD_TILE_5 = map_funcs.Point(1597, 197)
# Measured as the average of two points
RUNWAY_22_END_TILE_6 = map_funcs.Point((736 + 774) / 2, (1276 + 1306) / 2)
RUNWAY_22_END_TILE_7 = map_funcs.Point((1279 + 1319) / 2, (532 + 564) / 2)


THRESHOLD_ON_EACH_TILE: typing.Dict[int, map_funcs.Point] = {
    k: map_funcs.point_tile_to_tile(5, RUNWAY_22_THRESHOLD_TILE_5, k, TILE_OFFSETS) for k in TILE_FILES.keys()
}


# From a clear line across the runway on Tile 7
RUNWAY_WIDTH_PX = math.sqrt((1431 - 1473)**2 + (338 - 371)**2)


RUNWAY_LENGTH_HEADING = map_funcs.distance_bearing(
    RUNWAY_22_THRESHOLD_TILE_5,
    map_funcs.point_tile_to_tile(7, RUNWAY_22_END_TILE_7, 5, TILE_OFFSETS),
    TILE_SCALE_M_PER_PIXEL,
)


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
POSITIONS_FROM_TILES: typing.Dict[int, typing.Tuple[int, map_funcs.Point, str]] = {
    1: (1, map_funcs.Point(1207, 749), 'Edge of settlement in line with dark patch on island in the foreground.'),
    87: (1, map_funcs.Point(939, 1087), 'Settlement line with isolated lake and finger into lake.'),
    295: (2, map_funcs.Point(1164, 801), 'Trees and edge of V shaped lake.'),

    483: (3, map_funcs.Point(1258, 627), 'Blue roofed building in line with RHS of larger white building.'),
    555: (3, map_funcs.Point(1040, 903), 'Factory with covered conveyer belt.'),
    593: (3, map_funcs.Point(938, 1033), 'Tree line with red building behind.'),
    621: (3, map_funcs.Point(840, 1159), 'Blue building left lined up with low white building left.'),
    652: (3, map_funcs.Point(736, 1293), 'Crossing road with red building beyond.'),

    704: (4, map_funcs.Point(1246, 581), 'Crossing road with roundabout beyond.'),
    749: (4, map_funcs.Point(1105, 762), 'Crossing boundary fence.'),

    827: (5, map_funcs.Point(1597, 197), 'Crossing the threshold.'),
    # About 280px from threshold
    880: (5, map_funcs.Point(1444, 395), 'Start of the first set of white marker pairs.'),
    888: (5, map_funcs.Point(1418, 423), 'End of the first set of white marker pairs.'),
    932: (5, map_funcs.Point(1290, 585), 'Start of the second set of white marker pairs.'),
    940: (5, map_funcs.Point(1266, 615), 'End of the second set of white marker pairs.'),
}


SLAB_LENGTH = 6.0 # Width is 1.8

SLAB_TRANSITS: typing.Dict[int, typing.Tuple[int, float]] = {
    841: (2, 1.0),
    864: (8, 3.9),
    # Frame 880 shows a slab edge exactly at the start of the white bars
    # Frame 888 shows a slab edge exactly at the enf of the white bars
    # Bars are 36 pixels long, 9px/slab 9*0.6172839506172839 = 5.55
    880: (8, 4.0),
    895: (8, 4.0),
    918: (12, 5.9),
    # Frames 932-940 is 4 slabs across the bars, as above.
    964: (979-964, 7.0),
    # Touchdown is 1015
    1016: (1031 - 1016, 7.0),
    1053: (1064 - 1053, 5.0),
    1075: (1086 - 1075, 5.0),

    1106: (1115 - 1106, 4.0),
    1119: (1128 - 1119, 4.0),
    1151: (1160 - 1151, 4.0),
    1198: (1205 - 1198, 3.0),
    1222: (1227 - 1222, 2.0),
    1247: (1252 - 1247, 2.0),
    1262: (1267 - 1262, 2.0),
    1293: (1301 - 1293, 3.0),
    1323: (1329 - 1323, 2.2),
    1346: (1352 - 1346, 2.1),
    1370: (1373 - 1370, 1.0),
    # 1384 runway dissapears
}


FRAME_EVENTS: typing.Dict[int, str] = {
    1: 'Video start',
    827: 'Threshold',
    1015: 'Touchdown',
    max(SLAB_TRANSITS.keys()): 'Last speed measurement',
    1384: 'Runway disappears',
    1685: 'Impact with fence',
    1712: 'Final impact',
    1819: 'Last frame',
}

# Touchdown at about 00:35 [1015], 4 seconds after last position, say 4 * 85 = 340, add 330, so 670m from threshold
# Off runway at about 00:46 [1380], 11 seconds after that, 11 * 70 = 770, add 670, so 1440m from threshold, 200m to go.
# Crosses a pale track at 00:54, [1621], near boundary edge?
# Frame 1685 landing gear hits an obstruction and collapses, boundary fence?
# Breach fence and undercarridge collapse, tile 7, Point(970, 697)
# Frame 1712, camera movement indicates impact.
# Impact site is tile 7, Point(926, 737)
# Impact at 00:57.
FRAME_THRESHOLD = 827
FRAME_TOUCHDOWN = 1015  # Movement of camera due to impact.

FRAME_LAST = 1819


SLAB_SPEEDS = np.empty((len(SLAB_TRANSITS), 5))

for f, frame_number in enumerate(sorted(SLAB_TRANSITS.keys())):
    d_frame, d_slab = SLAB_TRANSITS[frame_number]
    t = map_funcs.frame_to_time(frame_number + d_frame / 2)
    dt = map_funcs.frames_to_dtime(frame_number, frame_number + d_frame)
    dx = d_slab * SLAB_LENGTH
    SLAB_SPEEDS[f][0] = frame_number
    SLAB_SPEEDS[f][1] = t
    SLAB_SPEEDS[f][2] = dx / dt
    SLAB_SPEEDS[f][3] = (dx + .5) / dt
    SLAB_SPEEDS[f][4] = (dx - .5) / dt
