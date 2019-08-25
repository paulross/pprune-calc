import itertools
import math
import pprint
import sys
import typing

import map_funcs

GOOGLE_EARTH_AIRPORT_IMAGES = {
    'GoogleEarth_AirportCamera_C.jpg' : {
        'path': 'video_images/GoogleEarth_AirportCamera_C.jpg',
        'width': 4800,
        'height': 3011,
        # Originally measured on the 100m legend as 181 px
        # 'm_per_px': 100 / (4786 - 4605),
        # Corrected to 185 to give runway length of 1650.5 m
        'm_per_px': 100 / (4786 - 4601),
        'datum': 'runway_23_start',
        'measurements': {
            # 'datum_1': 'runway_23_end',
            'runway_23_start': map_funcs.Point(3217, 204),
            'runway_23_end': map_funcs.Point((1310 + 1356) / 2, (2589 + 2625) / 2),
            'perimeter_fence': map_funcs.Point(967, 2788),
            'red_building': map_funcs.Point(914, 2827),
            'helicopter': map_funcs.Point(2630, 1236),
            'camera_B': map_funcs.Point(2890, 1103),
            'buildings_apron_edge': map_funcs.Point(2213, 1780),
            # The next three are from camera B frame 850
            # Dark smudge on right
            'right_dark_grass': map_funcs.Point(2742, 1137),
            # Pale smudge on right where tarmac meets grass
            'right_light_grass': map_funcs.Point(2755, 1154),
            # Pale smudge on left where tarmac taxiway meets grass
            # 'left_light_grass': map_funcs.Point(2492, 1488),
            # Bright roofed house
            'bright_roofed_house': map_funcs.Point(1067, 2243),
        }
    },
}

# This is an estimate of the absolute position error in metres of a single point in isolation.
ABSOLUTE_POSITION_ERROR_M = 10.0
# Points this close together have an accuracy of ABSOLUTE_POSITION_ERROR_M.
# If closer then the error is proportionally less.
# If further apart then the error is proportionally greater.
RELATIVE_POSITION_ERROR_BASELINE_M = 1000.0

RELATIVE_BEARING_ERROR_DEG = 0.5


def relative_position_error(distance_between: float) -> float:
    """This returns a relative position error estimate of two points separated by distance_between.
    It holds the idea that it is extremely unlikely that two points close together have extreme errors
    but as they separate the error is likely to be greater.
    """
    return ABSOLUTE_POSITION_ERROR_M * distance_between / RELATIVE_POSITION_ERROR_BASELINE_M


RUNWAY_LENGTH_M = map_funcs.distance(
    GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_23_start'],
    GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_23_end'],
    GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
)

RUNWAY_HEADING_DEG = map_funcs.bearing(
    GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_23_start'],
    GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_23_end'],
)


def measurements_relative_to_runway() -> typing.Dict[str, map_funcs.Point]:
    """Returns a dict of measurements in metres that are reduced to the runway axis."""
    ret: typing.Dict[str, map_funcs.Point] = {}
    datum_name = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['datum']
    origin = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'][datum_name]
    m_per_px = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    for k in GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']:
        pt = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'][k]
        new_pt = map_funcs.translate_rotate(pt, RUNWAY_HEADING_DEG, origin)
        ret[k] = map_funcs.Point(m_per_px * new_pt.x, m_per_px * new_pt.y)
    return ret


def bearings_from_camera_b() -> typing.Dict[str, float]:
    ret: typing.Dict[str, float] = {}
    camera_b = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['camera_B']
    m_per_px = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    for k, v in GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'].items():
        if k != 'camera_B':
            b = map_funcs.bearing(camera_b, v)
            b_min, b_max = map_funcs.bearing_min_max(camera_b, v, ABSOLUTE_POSITION_ERROR_M / m_per_px)
            ret[k] = b, b_min, b_max
    return ret


def main() -> int:
    # Check scale and runway length
    m_per_px = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    print(f'GoogleEarth_AirportCamera_C.jpg scale {m_per_px:0.4f} (m/pixel)')
    print(f'GoogleEarth_AirportCamera_C.jpg runway length {RUNWAY_LENGTH_M:.1f} (m)')
    print(f'GoogleEarth_AirportCamera_C.jpg runway heading {RUNWAY_HEADING_DEG:.2f} (degrees)')
    measurements = measurements_relative_to_runway()
    print('X-Y Relative')
    for k in measurements:
        print(f'{k:24} : x={measurements[k].x:8.1f} y={measurements[k].y:8.1f}')
    bearings = bearings_from_camera_b()
    print('Bearings')
    for k in bearings:
        # print(f'{k:24} : {bearings[k]:8.1f}')
        b, b_min, b_max = bearings[k]
        # print(f'{k:24} : {bearings[k]}')
        print(f'{k:24} : {b:8.2f} ± {b_max - b:.2f}/{b_min - b:.2f}')
    for a, b in itertools.combinations(('red_building', 'helicopter', 'buildings_apron_edge'), 2):
        ba, ba_min, ba_max = bearings[a]
        bb, bb_min, bb_max = bearings[b]
        print(a, '<->', b)
        print(f'{ba - bb:4.2f} {ba_max - bb_min:4.2f} {ba_min - bb_max:4.2f}')

    return 0


if __name__ == '__main__':
    sys.exit(main())