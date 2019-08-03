import typing

import numpy as np

import map_funcs

URL = 'https://youtu.be/LtJcgdU5MUk'
FRAME_RATE = 30

# Touchdown at about 00:35 [1015], 4 seconds after last position, say 4 * 85 = 340, add 330, so 670m from threshold
# Off runway at about 00:46 [1380], 11 seconds after that, 11 * 70 = 770, add 670, so 1440m from threshold, 200m to go.
# Crosses a pale track at 00:54, [1621], near boundary edge?
# Frame 1685 landing gear hits an obstruction and collapses, boundary fence?
# Breach fence and undercarridge collapse, tile 7, Point(970, 697)
# Frame 1712, camera movement indicates impact.
# Impact site is tile 7, Point(926, 737)
# Impact at 00:57.

# In metres
# DISTANCE_FROM_RUNWAY_END_TO_FENCE = 213.0
# DISTANCE_FROM_FENCE_TO_FINAL_IMPACT = 38.4
# DISTANCE_FROM_RUNWAY_END_TO_FINAL_IMPACT = DISTANCE_FROM_RUNWAY_END_TO_FENCE + DISTANCE_FROM_FENCE_TO_FINAL_IMPACT

FRAME_THRESHOLD = 827
FRAME_TOUCHDOWN = 1015  # Movement of camera due to impact.
FRAME_LAST = 1819

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

# The estimated error when counting slabs, 10% of slab length
SLAB_LENGTH = 6.0  # Width is 1.8
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
LAST_MEASURED_TIME = map_funcs.frame_to_time(LAST_MEASURED_FRAME, FRAME_RATE)


def init_slab_speeds():
    slab_speeds = np.empty((len(SLAB_TRANSITS), 5))
    for f, frame_number in enumerate(sorted(SLAB_TRANSITS.keys())):
        d_frame, d_slab = SLAB_TRANSITS[frame_number]
        dx = d_slab * SLAB_LENGTH
        t = map_funcs.frame_to_time(frame_number + d_frame / 2, FRAME_RATE)
        dt = map_funcs.frames_to_dtime(frame_number, frame_number + d_frame, FRAME_RATE)
        slab_speeds[f][0] = frame_number
        slab_speeds[f][1] = t
        slab_speeds[f][2] = dx / dt
        slab_speeds[f][3] = (dx + SLAB_MEASUREMENT_ERROR) / dt
        slab_speeds[f][4] = (dx - SLAB_MEASUREMENT_ERROR) / dt
    return slab_speeds


SLAB_SPEEDS = init_slab_speeds()

FRAME_EVENTS: typing.Dict[int, str] = {
    1: 'Video start',
    510: 'Maximum ground speed',
    827: 'Threshold',
    1015: 'Touchdown',
    map_funcs.time_to_frame(36.0, FRAME_RATE): 'Start of drift to the right.',
    LAST_MEASURED_FRAME: 'Last speed measurement',
    1384: 'Runway disappears',
    1685: 'Impact with fence',
    1712: 'Final impact?',
    1819: 'Last frame',
}

FRAME_EVENTS_STR_KEY = {v: k for k, v in FRAME_EVENTS.items()}

# This is the best accuracy that we can claim based on the comparison of differentiated tile data
# and the slab data
VIDEO_A_MAX_SPEED_ACCURACY = 2.0
