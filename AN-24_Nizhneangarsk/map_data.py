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


#======== Slab meaasurements ========

SLAB_LENGTH = 6.0  # Width is 1.8

# The estimated error when counting slabs, 10% of slab length
SLAB_MEASUREMENT_ERROR = SLAB_LENGTH * 0.1

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

LAST_MEASURED_FRAME = max(SLAB_TRANSITS.keys()) + SLAB_TRANSITS[max(SLAB_TRANSITS.keys())][0]
LAST_MEASURED_TIME = map_funcs.frame_to_time(LAST_MEASURED_FRAME)

SLAB_SPEEDS = np.empty((len(SLAB_TRANSITS), 5))

for f, frame_number in enumerate(sorted(SLAB_TRANSITS.keys())):
    d_frame, d_slab = SLAB_TRANSITS[frame_number]
    t = map_funcs.frame_to_time(frame_number + d_frame / 2)
    dt = map_funcs.frames_to_dtime(frame_number, frame_number + d_frame)
    dx = d_slab * SLAB_LENGTH
    SLAB_SPEEDS[f][0] = frame_number
    SLAB_SPEEDS[f][1] = t
    SLAB_SPEEDS[f][2] = dx / dt
    SLAB_SPEEDS[f][3] = (dx + SLAB_MEASUREMENT_ERROR) / dt
    SLAB_SPEEDS[f][4] = (dx - SLAB_MEASUREMENT_ERROR) / dt


# After the aircraft departs the runway we have no data. There are some events though.
BOUNDARY_FENCE_TILE_7 = map_funcs.Point(988, 713)
FINAL_BUILDING_TILE_7 = map_funcs.Point(934, 743)
BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M = TILE_SCALE_M_PER_PIXEL * math.sqrt(
    (THRESHOLD_ON_EACH_TILE[7].x - BOUNDARY_FENCE_TILE_7.x)**2
    + (THRESHOLD_ON_EACH_TILE[7].y - BOUNDARY_FENCE_TILE_7.y)**2
)
FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M = TILE_SCALE_M_PER_PIXEL * math.sqrt(
    (THRESHOLD_ON_EACH_TILE[7].x - FINAL_BUILDING_TILE_7.x)**2
    + (THRESHOLD_ON_EACH_TILE[7].y - FINAL_BUILDING_TILE_7.y)**2
)

# In metres
# DISTANCE_FROM_RUNWAY_END_TO_FENCE = 213.0
# DISTANCE_FROM_FENCE_TO_FINAL_IMPACT = 38.4
# DISTANCE_FROM_RUNWAY_END_TO_FINAL_IMPACT = DISTANCE_FROM_RUNWAY_END_TO_FENCE + DISTANCE_FROM_FENCE_TO_FINAL_IMPACT


FRAME_EVENTS: typing.Dict[int, str] = {
    1: 'Video start',
    510: 'Maximum ground speed',
    827: 'Threshold',
    1015: 'Touchdown',
    map_funcs.time_to_frame(36.0): 'Start of drift to the right.',
    LAST_MEASURED_FRAME: 'Last speed measurement',
    1384: 'Runway disappears',
    1685: 'Impact with fence',
    1712: 'Final impact?',
    1819: 'Last frame',
}


# This is the best accuracy that we can claim based on the comparison of differentiated tile data
# and the slab data
MAX_SPEED_ACCURACY = 2.0


#============ Video from the security camera =====


#------------ Google earth image ------------
GOOGLE_EARTH_AIRPORT_IMAGES = {
    'GoogleEarth_AirportCamera_C.jpg' : {
        'path': 'video_images/GoogleEarth_AirportCamera_C.jpg',
        'width': 4800,
        'height': 3011,
        # Originally measured on the 100m legend as 181 px
        # 'm_per_px': 100 / (4786 - 4605),
        # Corrected to 185 to give runway length of 1650.5 m
        'm_per_px': 100 / (4786 - 4601),
        'datum': 'runway_22_start',
        'measurements': {
            # 'datum_1': 'runway_22_end',
            'runway_22_start': map_funcs.Point(3217, 204),
            'runway_22_end': map_funcs.Point((1310 + 1356) / 2, (2589 + 2625) / 2),
            'perimeter_fence': map_funcs.Point(967, 2788),
            'red_building': map_funcs.Point(914, 2827),
            'helicopter': map_funcs.Point(2630, 1236),
            'camera_A': map_funcs.Point(2890, 1103),
        }
    },
}

# Check scale and runway length
print('GoogleEarth_AirportCamera_C.jpg scale', GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'])
print('GoogleEarth_AirportCamera_C.jpg runway length',
    map_funcs.distance(
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_end'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
    ),
    RUNWAY_LENGTH_HEADING[0],
)
print('GoogleEarth_AirportCamera_C.jpg runway heading',
    map_funcs.bearing(
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_end'],
    ),
    RUNWAY_LENGTH_HEADING[1],
)
print('GoogleEarth_AirportCamera_C.jpg perimeter_fence',
    map_funcs.distance(
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['perimeter_fence'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
    ),
)
print('GoogleEarth_AirportCamera_C.jpg red_building',
    map_funcs.distance(
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['red_building'],
        GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
    ),
)

for k in GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'].keys():
    datum_name = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['datum']
    pt = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'][k]
    origin = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'][datum_name]
    m_per_px = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    new_pt = map_funcs.translate_rotate(pt, 218.09715488381195, origin)
    # print('Rotated', k, new_pt, new_pt.x * m_per_px, new_pt.y * m_per_px)
    print(
        f'Rotated: {k:20}'
        f' Old {pt.x:8.1f} {pt.y:8.1f}'
        f' New {new_pt.x:8.1f} {new_pt.y:8.1f}'
        f' In m {m_per_px * new_pt.x:8.1f} {m_per_px * new_pt.y:8.1f}'
    )


#------------ END: Google earth image ------------

#------------ Security Camera A ------------


SECURITY_CAMERA_A_FILE = 'video_images/AirportCamera.mp4'
SECURITY_CAMERA_A_FRAMES = 'video_images/AirportCamera_frames'

SECURITY_CAMERA_A_FRAME_RATE = 25

SECURITY_CAMERA_A_FRAME_FIRST_APPEARANCE = 36
SECURITY_CAMERA_A_FRAME_HELICOPTER_TRANSIT = 86

print('Helicopter transit time', (SECURITY_CAMERA_A_FRAME_HELICOPTER_TRANSIT - SECURITY_CAMERA_A_FRAME_FIRST_APPEARANCE) / SECURITY_CAMERA_A_FRAME_RATE)

# Rough estimate of distance and video time when the aircraft transits the helicopter.
# Transit position is Point(2262, 1170)
# Runway start is (3210, 103)
# Runway end is (1066.5, 2508.0)
# Runway length is math.sqrt((3210-1066.5)**2 + (2508-103)**2)) == 3221.6


class AircraftExtremities(typing.NamedTuple):
    left_tip: map_funcs.Point
    right_tip: map_funcs.Point
    nose: map_funcs.Point
    tail: map_funcs.Point
    fin_tip: map_funcs.Point
    fin_gnd: map_funcs.Point

    def aspect(self, span: float, length: float) -> float:
        """Returns the aspect in degrees given the original span and length."""
        dy = self.left_tip.y - self.right_tip.y
        dx = self.left_tip.x - self.right_tip.x
        s_dash = math.sqrt(dx ** 2 + dy ** 2)
        # s_dash is +ve if right wing tip is to the left of the left wing tip
        if dx < 0:
            s_dash = -s_dash
        dy = self.nose.y - self.tail.y
        dx = self.nose.x - self.tail.x
        l_dash = math.sqrt(dx ** 2 + dy ** 2)
        # s_dash is +ve if right wing tip is to the left of the left wing tip
        if dx < 0:
            l_dash = -l_dash
        # print(s_dash, l_dash)
        aspect = math.atan2(l_dash * span, s_dash * length)
        return math.degrees(aspect) % 360


    # TODO: Methods to compute the aspect, range, error etc.


# Source: https://en.wikipedia.org/wiki/Antonov_An-24
ANTONOV_AN_24_SPAN = 29.2
ANTONOV_AN_24_LENGTH = 23.53
ANTONOV_AN_24_HEIGHT = 8.32


# The key is the frame number
SECURITY_CAMERA_A_ASPECTS: typing.Dict[int, AircraftExtremities] = {
    44: AircraftExtremities(
        # Span left-right
        map_funcs.Point(513, 110),
        map_funcs.Point(604, 112),
        # Nose-tail
        map_funcs.Point(550, 120),
        map_funcs.Point(592, 117),
        # Fin tip to ground
        map_funcs.Point(590, 88),
        map_funcs.Point(589, 132),
    ),
    50: AircraftExtremities(
        # Span left-right
        map_funcs.Point(472, 111),
        map_funcs.Point(559, 110),
        # Nose-tail
        map_funcs.Point(508, 119),
        map_funcs.Point(545, 116),
        # Fin tip to ground
        map_funcs.Point(545, 89),
        map_funcs.Point(545, 129),
    ),
    55: AircraftExtremities(
        # Span left-right
        map_funcs.Point(449, 110),
        map_funcs.Point(536, 115),
        # Nose-tail
        map_funcs.Point(486, 117),
        map_funcs.Point(519, 117),
        # Fin tip to ground
        map_funcs.Point(520, 90),
        map_funcs.Point(519, 127),
    ),
    60: AircraftExtremities(
        # Span left-right
        map_funcs.Point(424, 110),
        map_funcs.Point(507, 115),
        # Nose-tail
        # Looks error prone
        map_funcs.Point(457, 116),
        map_funcs.Point(487, 115),
        # Fin tip to ground
        map_funcs.Point(487, 89),
        map_funcs.Point(487, 127),
    ),
    # This is where the aircraft is transiting the parked helicopter
    84: AircraftExtremities(
        # Span left-right
        map_funcs.Point(324, 109),
        map_funcs.Point(393, 114),
        # Nose-tail
        # Looks error prone
        map_funcs.Point(349, 115),
        map_funcs.Point(375, 115),
        # Fin tip to ground
        map_funcs.Point(375, 92),
        map_funcs.Point(374, 122),
    ),
}

print('Aspects:')
for k in sorted(SECURITY_CAMERA_A_ASPECTS.keys()):
    mid_span = map_funcs.mid_point(
        SECURITY_CAMERA_A_ASPECTS[k].left_tip,
        SECURITY_CAMERA_A_ASPECTS[k].right_tip,
    )
    mid_length = map_funcs.mid_point(
        SECURITY_CAMERA_A_ASPECTS[k].nose,
        SECURITY_CAMERA_A_ASPECTS[k].tail,
    )
    mid_point = map_funcs.mid_point(mid_span, mid_length)
    aspect = SECURITY_CAMERA_A_ASPECTS[k].aspect(ANTONOV_AN_24_SPAN, ANTONOV_AN_24_LENGTH)
    print(f'{k:3d} aspect={aspect:5.3f} x: {mid_point.x:6.2f} y: {mid_point.y:6.2f}')


print('Aspects from tail height:')
for k in sorted(SECURITY_CAMERA_A_ASPECTS.keys()):
    span_px = map_funcs.distance(
        SECURITY_CAMERA_A_ASPECTS[k].left_tip,
        SECURITY_CAMERA_A_ASPECTS[k].right_tip,
        1,
    ) / ANTONOV_AN_24_SPAN
    m_per_pixel = ANTONOV_AN_24_HEIGHT / map_funcs.distance(
        SECURITY_CAMERA_A_ASPECTS[k].fin_tip,
        SECURITY_CAMERA_A_ASPECTS[k].fin_gnd,
        1,
    )
    apparent_span_m = m_per_pixel * span_px
    aspect = 90 - math.degrees(math.asin(apparent_span_m / ANTONOV_AN_24_SPAN))
    print(f'{k:3d} span={span_px:5.3f} (px) m/px: {m_per_pixel:6.3f} aspect: {aspect:6.2f}')

