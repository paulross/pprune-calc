"""
Data from video B, a fixed camera.
"""
import itertools
import math
import sys
import typing

import numpy as np
from scipy.optimize import curve_fit

import map_funcs
from cmn import polynomial
from common import structs
from data import aircraft, google_earth
from data.aircraft import ANTONOV_AN_24_SPAN, ANTONOV_AN_24_LENGTH, ANTONOV_AN_24_HEIGHT
# import data.google_earth

#------------ Security Camera as Video B ------------
URL = 'https://youtu.be/BQ8ujmRhLH0'

VIDEO_FILE = 'video_images/AirportCamera.mp4'
FRAMES_DIRECTORY = 'video_images/AirportCamera_frames'
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 350
FRAME_RATE = 25


def frame_to_time(frame: int) -> float:
    """Return the time in seconds from the start of this video."""
    return map_funcs.frame_to_time(frame, FRAME_RATE)


CAMERA_POSITION_ON_GOOGLE_EARTH = (
    google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['camera_B']
)

# Camera position relative ot runway, x is metres from runway 22 start, y is metres from runway centreline (+ve right)
CAMERA_POSITION_XY = map_funcs.xy_from_two_points_and_axis(
    google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
    CAMERA_POSITION_ON_GOOGLE_EARTH,
    google_earth.RUNWAY_HEADING_DEG,
    google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
)

# Specific frame events
FRAME_EVENTS: typing.Dict[int, str] = {
    36: 'First appearance',
    42: 'Tyre smoke and dust',
    86: 'Helicopter transit',
    96: 'Increase in tyre smoke',
    290: 'Start of large dust plume',
    # This is estimated as 1 second before the black smoke starts appearing
    23 * FRAME_RATE + 1: 'Start of smoke plume'
}

FRAME_EVENTS_STR_KEY = {v: k for k, v in FRAME_EVENTS.items()}

# In frame 850 these are the positions of objects observable on google earth
FRAME_850_POSITIONS: typing.Dict[str, map_funcs.Point] = {
    # Dark smudge on right
    # 'right_dark_grass': map_funcs.Point(625, 173),
    # Pale smudge on right where tarmac meets grass
    'right_light_grass': map_funcs.Point(485, 164),
    # Pale smudge on left where tarmac taxiway meets grass
    # 'left_light_grass': map_funcs.Point(32, 112),
    # Bright roofed house, slightly dubious connection.
    'bright_roofed_house': map_funcs.Point(277, 75),
    # Mi-2 helicopter
    'helicopter': map_funcs.Point(356, 111),
    # Some structures on the extreme left
    'buildings_apron_edge': map_funcs.Point(12, 101),
    # Estimated from the base of the dark smoke column.
    'red_building': map_funcs.Point(75, 90),
}
FRAME_850_HELICOPTER_HEIGHT_PIXELS = 30
FRAME_850_HELICOPTER_LENGTH_PIXELS = 68
FRAME_850_ERROR_PIXELS = 2

assert all(
    [
        k in google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
            for k in FRAME_850_POSITIONS.keys()
    ]
)


class PixelsPerDegreeBetweenAB(typing.NamedTuple):
    name_a: str
    name_b: str
    delta_pixels: int
    delta_bearing: float
    pixels_per_degree: float


def _pixels_per_degree_between_points() -> typing.List[PixelsPerDegreeBetweenAB]:
    """With the FRAME_850_POSITIONS and the data.google_earth bearings computed from relative positions
    then return an estimate of the number of pixels per degree of arc.

    Example::

        helicopter               <-> buildings_apron_edge     dx:  344 db: 17.9 px_per_degree= 19.21
        helicopter               <-> red_building             dx:  281 db: 14.0 px_per_degree= 20.05
        buildings_apron_edge     <-> red_building             dx:  -63 db: -3.9 px_per_degree= 16.17
        By helicopter height:  22.04  24.98  19.10
        By helicopter length:  18.11  19.18  17.05
        Mid  :  19.12 ±: 2.9/-2.9
        Plus :  20.23 ±: 4.8/-3.0
        Minus:  18.01 ±: 1.8/-2.9
        Mean of all  19.12
        Max of all   24.98   5.86
        Min of all   15.14  -3.98

    """
    ge_measurements = google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
    m_per_px = google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    ret = []
    for key_a, key_b in itertools.combinations(FRAME_850_POSITIONS.keys(), 2):
        google_earth_position_a = ge_measurements[key_a]
        google_earth_position_b = ge_measurements[key_b]
        dist_brng_a = map_funcs.distance_bearing(
            CAMERA_POSITION_ON_GOOGLE_EARTH,
            google_earth_position_a,
            m_per_px,
        )
        dist_brng_b = map_funcs.distance_bearing(
            CAMERA_POSITION_ON_GOOGLE_EARTH,
            google_earth_position_b,
            m_per_px,
        )
        frame_position_a = FRAME_850_POSITIONS[key_a]
        frame_position_b = FRAME_850_POSITIONS[key_b]
        dx = frame_position_a.x - frame_position_b.x
        db = dist_brng_a[1] - dist_brng_b[1]
        px_per_degree = dx / db
        ret.append(PixelsPerDegreeBetweenAB(key_a, key_b, dx, db, px_per_degree))
    return ret


class PixelsPerDegreeMidPlusMinus(typing.NamedTuple):
    pixels_degree: typing.List[float]
    pixels_degree_plus: typing.List[float]
    pixels_degree_minus: typing.List[float]


def _pixels_per_degree_all_measurements() -> PixelsPerDegreeMidPlusMinus:
    ge_measurements = google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
    m_per_px = google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    pixels_degree = []
    pixels_degree_plus = []
    pixels_degree_minus = []
    for value in _pixels_per_degree_between_points():
        pixels_degree.append(value.pixels_per_degree)
        if value.delta_pixels > 0:
            pixels_degree_plus.append((value.delta_pixels + 2 * FRAME_850_ERROR_PIXELS) / value.delta_bearing)
            pixels_degree_minus.append((value.delta_pixels - 2 * FRAME_850_ERROR_PIXELS) / value.delta_bearing)
        else:
            pixels_degree_plus.append((value.delta_pixels - 2 * FRAME_850_ERROR_PIXELS) / value.delta_bearing)
            pixels_degree_minus.append((value.delta_pixels + 2 * FRAME_850_ERROR_PIXELS) / value.delta_bearing)
    # By helicopter dimensions
    helicopter_distance, helicopter_bearing = map_funcs.distance_bearing(
            CAMERA_POSITION_ON_GOOGLE_EARTH,
            ge_measurements['helicopter'],
            m_per_px,
        )
    angle_helicopter_height = math.degrees(2 * math.atan2(aircraft.MI_2_HEIGHT, 2 * helicopter_distance))
    pixels_degree.append(FRAME_850_HELICOPTER_HEIGHT_PIXELS / angle_helicopter_height)
    pixels_degree_plus.append((FRAME_850_HELICOPTER_HEIGHT_PIXELS + 2 * FRAME_850_ERROR_PIXELS) / angle_helicopter_height)
    pixels_degree_minus.append((FRAME_850_HELICOPTER_HEIGHT_PIXELS - 2 * FRAME_850_ERROR_PIXELS) / angle_helicopter_height)
    # print(f'By helicopter height: {pixels_degree[-1]:6.2f} {pixels_degree_plus[-1]:6.2f} {pixels_degree_minus[-1]:6.2f}')
    angle_helicopter_length = math.degrees(2 * math.atan2(aircraft.MI_2_LENGTH, 2 * helicopter_distance))
    # Correct for aspect
    aspect = helicopter_bearing - google_earth.RUNWAY_HEADING_DEG
    angle_helicopter_length *= math.cos(math.radians(aspect))
    pixels_degree.append(FRAME_850_HELICOPTER_LENGTH_PIXELS / angle_helicopter_length)
    pixels_degree_plus.append((FRAME_850_HELICOPTER_LENGTH_PIXELS + 2 * FRAME_850_ERROR_PIXELS)/ angle_helicopter_length)
    pixels_degree_minus.append((FRAME_850_HELICOPTER_LENGTH_PIXELS - 2 * FRAME_850_ERROR_PIXELS)/ angle_helicopter_length)
    return PixelsPerDegreeMidPlusMinus(pixels_degree, pixels_degree_plus, pixels_degree_minus)


def _pixels_per_degree_sum_count_mean_min_max():
    pixels_degree, pixels_degree_plus, pixels_degree_minus = _pixels_per_degree_all_measurements()
    values_sum = 0.0
    values_count = 0
    values_min = sys.float_info.max
    values_max = sys.float_info.min
    for name, pd in zip(('Mid', 'Plus', 'Minus'), (pixels_degree, pixels_degree_plus, pixels_degree_minus)):
        values_sum += sum(pd)
        values_count += len(pd)
        values_min = min(values_min, min(pd))
        values_max = max(values_max, max(pd))
    values_mean = values_sum / values_count
    return values_sum, values_count, values_mean, values_min, values_max


def pixels_per_degree():
    values_sum, values_count, values_mean, values_min, values_max = _pixels_per_degree_sum_count_mean_min_max()
    px_per_degree_mean = values_sum / values_count
    px_per_degree_error = px_per_degree_mean / 10.0
    # TODO: the -1 is experimental to get the speeds to match video A
    return px_per_degree_mean +2.25, px_per_degree_error


PX_PER_DEGREE, PX_PER_DEGREE_ERROR = pixels_per_degree()


def print_pixels_per_degree_data():
    print('print_pixels_per_degree_data()')
    for value in _pixels_per_degree_between_points():
        print(
            f'{value.name_a:24} <-> {value.name_b:24}'
            f' dx: {value.delta_pixels:4d} db: {value.delta_bearing:4.1f}'
            f' px_per_degree={value.pixels_per_degree:6.2f}'
        )
    pixels_degree, pixels_degree_plus, pixels_degree_minus = _pixels_per_degree_all_measurements()
    for name, pd in zip(('Mid', 'Plus', 'Minus'), (pixels_degree, pixels_degree_plus, pixels_degree_minus)):
        # pd.sort()
        # print(' '.join([f'{p:6.2f}' for p in pd]))
        print(
            f'{name:5}: {sum(pd) / len(pd):6.2f}'
            f' ±: {max(pd) - (sum(pd) / len(pd)):.1f}'
            f'/{min(pd) - (sum(pd) / len(pd)):.1f}'
        )
    values_sum, values_count, values_mean, values_min, values_max = _pixels_per_degree_sum_count_mean_min_max()
    print(f'Mean of all {values_mean:6.2f}')
    print(f' Max of all {values_max:6.2f} {values_max - values_mean:6.2f}')
    print(f' Min of all {values_min:6.2f} {values_min - values_mean:6.2f}')
    print(
        f'Definitive value for pixels/degree: {PX_PER_DEGREE:.1f} ±{PX_PER_DEGREE_ERROR:.1f} (pixels/degree)'
    )


def focal_length():
    degrees_widths = (
        VIDEO_WIDTH / PX_PER_DEGREE,
        VIDEO_WIDTH / (PX_PER_DEGREE + PX_PER_DEGREE_ERROR),
        VIDEO_WIDTH / (PX_PER_DEGREE - PX_PER_DEGREE_ERROR),
    )
    focal_lengths = (
        (36. / 2) / math.tan(math.radians(v / 2.0)) for v in degrees_widths
    )
    return structs.MidPlusMinus(*focal_lengths)


def _camera_axis_bearings():
    ret = {}
    ge_measurements = google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
    m_per_px = google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    for k in FRAME_850_POSITIONS.keys():
        google_earth_position = ge_measurements[k]
        dist_brng = map_funcs.distance_bearing(
            CAMERA_POSITION_ON_GOOGLE_EARTH,
            google_earth_position,
            m_per_px,
        )
        frame_position_a = FRAME_850_POSITIONS[k]
        these_camera_bearings = (
            dist_brng[1] + (VIDEO_WIDTH / 2.0 - frame_position_a.x) / PX_PER_DEGREE,
            dist_brng[1] + (VIDEO_WIDTH / 2.0 - frame_position_a.x) / (PX_PER_DEGREE + PX_PER_DEGREE_ERROR),
            dist_brng[1] + (VIDEO_WIDTH / 2.0 - frame_position_a.x) / (PX_PER_DEGREE - PX_PER_DEGREE_ERROR),
        )
        ret[k] = these_camera_bearings
    return ret


def _camera_axis_bearing_mean_min_max():
    camera_bearings = []
    camera_bearing_min = sys.float_info.max
    camera_bearing_max = sys.float_info.min
    bearings = _camera_axis_bearings()
    for k in bearings:
        these_camera_bearings = bearings[k]
        camera_bearings.append(these_camera_bearings[0])
        camera_bearing_min = min(camera_bearing_min, *these_camera_bearings)
        camera_bearing_max = max(camera_bearing_max, *these_camera_bearings)
    camera_bearing_mean = sum(camera_bearings) / len(camera_bearings)
    return camera_bearing_mean, camera_bearing_min, camera_bearing_max


def camera_axis_bearing():
    """
    """
    camera_bearing_mean, camera_bearing_min, camera_bearing_max = _camera_axis_bearing_mean_min_max()
    camera_bearing_error = (camera_bearing_max - camera_bearing_min) / 2
    # TODO: the +1 is experimental to get the speeds to match video A
    return camera_bearing_mean -1.75, camera_bearing_error


CAMERA_BEARING, CAMERA_BEARING_ERROR = camera_axis_bearing()


def bearing_x_degrees(p: int, px_per_degree_error: float=0.0) -> float:
    """Returns the bearing of the x pixel in degrees."""
    db = (p - VIDEO_WIDTH / 2.0) / (PX_PER_DEGREE + px_per_degree_error)
    return CAMERA_BEARING + db


def range_to_target(dp: float, s: float) -> float:
    """Given the distance in pixels and the actual distance s in metres this returns the range."""
    alpha_deg = dp / PX_PER_DEGREE
    d = s / (2 * math.tan(math.radians(alpha_deg / 2)))
    return d


def xy_from_range_bearing(range: float, bearing: float) -> map_funcs.Point:
    theta = bearing - google_earth.RUNWAY_HEADING_DEG
    # x = CAMERA_POSITION_ON_GOOGLE_EARTH


def print_camera_axis_bearing_data():
    print('print_camera_axis_bearing_data():')
    bearings = _camera_axis_bearings()
    for k in bearings:
        these_camera_bearings = bearings[k]
        # print('TRACE:', these_camera_bearings)
        print(
            f'{k:24} centre line bearing: {these_camera_bearings[0]:4.2f}'
            f' ± {these_camera_bearings[1] - these_camera_bearings[0]:.2f}'
            f'/{these_camera_bearings[2] - these_camera_bearings[0]:.2f}'
        )
    camera_bearing_mean, camera_bearing_min, camera_bearing_max = _camera_axis_bearing_mean_min_max()
    camera_bearing_error = (camera_bearing_max - camera_bearing_min) / 2
    print(
        f'Camera bearing: mean: {camera_bearing_mean:6.2f} ±{camera_bearing_error:.2f}'
        f' Worst case: ±{camera_bearing_max - camera_bearing_mean:.2f}'
        f'/{camera_bearing_min - camera_bearing_mean:.2f}'
    )
    print(
        f'Definitive value for the bearing of camera B axis: {CAMERA_BEARING:.1f} ±{CAMERA_BEARING_ERROR:.1f} (degrees)'
    )
    print(f'Bearing left: {bearing_x_degrees(0):.1f} right: {bearing_x_degrees(VIDEO_WIDTH):.1f}')


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


AIRCRAFT_ASPECTS: typing.Dict[int, AircraftExtremities] = {
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
    68: AircraftExtremities(
        # Span left-right
        map_funcs.Point(384, 109),
        map_funcs.Point(470, 114),
        # Nose-tail
        # Looks error prone
        map_funcs.Point(410, 119),
        map_funcs.Point(448, 115),
        # Fin tip to ground
        map_funcs.Point(448, 93),
        map_funcs.Point(448, 127),
    ),
    # This is where the aircraft is transiting the parked helicopter
    84: AircraftExtremities(
        # Span left-right
        map_funcs.Point(324, 109), map_funcs.Point(393, 114),
        # Nose-tail, looks error prone
        map_funcs.Point(349, 115), map_funcs.Point(375, 115),
        # Fin tip to ground
        map_funcs.Point(375, 92), map_funcs.Point(374, 122),
    ),
    93: AircraftExtremities(
        # Span left-right
        map_funcs.Point(287, 108), map_funcs.Point(362, 113),
        # Nose-tail, looks error prone
        map_funcs.Point(308, 116), map_funcs.Point(335, 116),
        # Fin tip to ground
        map_funcs.Point(336, 94), map_funcs.Point(335, 122),
    ),
    100: AircraftExtremities(
        # Span left-right
        map_funcs.Point(264, 108), map_funcs.Point(333, 112),
        # Nose-tail, looks error prone
        map_funcs.Point(268, 115), map_funcs.Point(311, 114),
        # Fin tip to ground
        map_funcs.Point(312, 95), map_funcs.Point(312, 121),
    ),
    110: AircraftExtremities(
        # Span left-right
        map_funcs.Point(241, 108), map_funcs.Point(305, 112),
        # Nose-tail, looks error prone
        map_funcs.Point(264, 115), map_funcs.Point(285, 115),
        # Fin tip to ground
        map_funcs.Point(285, 95), map_funcs.Point(286, 121),
    ),
    120: AircraftExtremities(
        # Span left-right
        map_funcs.Point(219, 108), map_funcs.Point(279, 112),
        # Nose-tail, looks error prone
        map_funcs.Point(237, 114), map_funcs.Point(256, 113),
        # Fin tip to ground
        map_funcs.Point(258, 96), map_funcs.Point(258, 120),
    ),
    130: AircraftExtremities(
        # Span left-right
        map_funcs.Point(201, 109), map_funcs.Point(259, 112),
        # Nose-tail, looks error prone
        map_funcs.Point(220, 114), map_funcs.Point(238, 113),
        # Fin tip to ground
        map_funcs.Point(239, 96), map_funcs.Point(239, 120),
    ),
    140: AircraftExtremities(
        # Span left-right
        map_funcs.Point(187, 108), map_funcs.Point(240, 111),
        # Nose-tail, looks error prone
        map_funcs.Point(202, 114), map_funcs.Point(223, 113),
        # Fin tip to ground
        map_funcs.Point(223, 97), map_funcs.Point(223, 119),
    ),
    150: AircraftExtremities(
        # Span left-right
        map_funcs.Point(170, 108), map_funcs.Point(218, 110),
        # Nose-tail, looks error prone
        map_funcs.Point(184, 114), map_funcs.Point(202, 113),
        # Fin tip to ground
        map_funcs.Point(202, 97), map_funcs.Point(203, 119),
    ),
    # TODO: Fill in
    231: AircraftExtremities(
        # Span left-right
        map_funcs.Point(93, 111), map_funcs.Point(122, 111),
        # Nose-tail, looks error prone
        map_funcs.Point(103, 114), map_funcs.Point(112, 113),
        # Fin tip to ground
        map_funcs.Point(112, 104), map_funcs.Point(113, 118),
    ),
    # TODO: Fill in
    312: AircraftExtremities(
        # Span left-right
        map_funcs.Point(56, 109), map_funcs.Point(78, 110),
        # Nose-tail, looks error prone
        map_funcs.Point(64, 111), map_funcs.Point(71, 112),
        # Fin tip to ground
        map_funcs.Point(71, 106), map_funcs.Point(71, 115),
    ),
}

AIRCRAFT_ASPECTS_ERROR_PIXELS = 2


def print_aspects() -> None:
    """This does not seem to be a useful/reliable/accurate calculation compared to others."""
    print('Aspects:')
    for k in sorted(AIRCRAFT_ASPECTS.keys()):
        mid_span = map_funcs.mid_point(
            AIRCRAFT_ASPECTS[k].left_tip,
            AIRCRAFT_ASPECTS[k].right_tip,
        )
        mid_length = map_funcs.mid_point(
            AIRCRAFT_ASPECTS[k].nose,
            AIRCRAFT_ASPECTS[k].tail,
        )
        mid_point = map_funcs.mid_point(mid_span, mid_length)
        aspect = AIRCRAFT_ASPECTS[k].aspect(ANTONOV_AN_24_SPAN, ANTONOV_AN_24_LENGTH)
        print(f'{k:3d} aspect={aspect :5.3f} x: {mid_point.x:6.2f} y: {mid_point.y:6.2f}')

    print('Aspects from tail height:')
    for k in sorted(AIRCRAFT_ASPECTS.keys()):
        span_px = map_funcs.distance(
            AIRCRAFT_ASPECTS[k].left_tip,
            AIRCRAFT_ASPECTS[k].right_tip,
            1,
        ) / ANTONOV_AN_24_SPAN
        m_per_pixel = ANTONOV_AN_24_HEIGHT / map_funcs.distance(
            AIRCRAFT_ASPECTS[k].fin_tip,
            AIRCRAFT_ASPECTS[k].fin_gnd,
            1,
        )
        apparent_span_m = m_per_pixel * span_px
        aspect = 90 - math.degrees(math.asin(apparent_span_m / ANTONOV_AN_24_SPAN))
        print(f'{k:3d} span={span_px :5.3f} (px) m/px: {m_per_pixel :6.3f} aspect: {aspect :6.2f}')


def print_aircraft_bearings_and_ranges():
    """Takes the AIRCRAFT_ASPECTS and the camera data to print bearing and ranges of the aircraft."""
    print('print_aircraft_bearings_and_ranges():')
    t_prev = None
    x_prev = None
    for frame in sorted(AIRCRAFT_ASPECTS):
        # Compute mid point of span
        mid_span = map_funcs.mid_point(
            AIRCRAFT_ASPECTS[frame].left_tip,
            AIRCRAFT_ASPECTS[frame].right_tip,
        )
        brg_deg = bearing_x_degrees(mid_span.x)
        # Compute height of tail
        tail_height_px = map_funcs.distance(AIRCRAFT_ASPECTS[frame].fin_gnd, AIRCRAFT_ASPECTS[frame].fin_tip, 1.0)
        tail_height_deg = tail_height_px / PX_PER_DEGREE
        range = range_to_target(tail_height_px, aircraft.ANTONOV_AN_24_HEIGHT)
        # Compute x, y relative to runway
        theta_deg = brg_deg - google_earth.RUNWAY_HEADING_DEG
        x = CAMERA_POSITION_XY.x + range * math.cos(math.radians(theta_deg))
        y = CAMERA_POSITION_XY.y + range * math.sin(math.radians(theta_deg))
        t = frame_to_time(frame)
        if t_prev is not None:
            dt = t - t_prev
            dx = x - x_prev
            dx_dt = dx / dt
        else:
            dt = 0.0
            dx = 0.0
            dx_dt = 0.0
        print(f'{frame:4d} {t:6.2f} {brg_deg:6.2f} {tail_height_deg:6.2f}'
              f' {range:6.1f} {x:6.2f} {y:6.2f} {dt:6.2f} {dx:6.2f} {dx_dt:6.2f}')
        t_prev = t
        x_prev = x


def print_aircraft_bearings_and_x():
    """Takes the AIRCRAFT_ASPECTS and the camera data to print bearings of the aircraft."""
    print('print_aircraft_bearings_and_x():')
    t_prev = None
    x_prev = None
    print(f'{"Frame":>6s} {"t":>6s} {"brg":>6s}'
          f' {"x":>6s} {"dt":>6s} {"dx":>6s} {"dx/dt":>6s}')
    for frame in sorted(AIRCRAFT_ASPECTS):
        # Compute mid point of span
        mid_span = map_funcs.mid_point(
            AIRCRAFT_ASPECTS[frame].left_tip,
            AIRCRAFT_ASPECTS[frame].right_tip,
        )
        brg_deg = bearing_x_degrees(mid_span.x)
        # Compute x, y relative to runway
        theta_deg = brg_deg - google_earth.RUNWAY_HEADING_DEG
        x = CAMERA_POSITION_XY.x - CAMERA_POSITION_XY.y * math.tan(math.radians(90 - theta_deg))
        t = frame_to_time(frame)
        if t_prev is not None:
            dt = t - t_prev
            dx = x - x_prev
            dx_dt = dx / dt
        else:
            dt = 0.0
            dx = 0.0
            dx_dt = 0.0
        print(f'{frame:6d} {t:6.2f} {brg_deg:6.2f}'
              f' {x:6.1f} {dt:6.2f} {dx:6.2f} {dx_dt:6.2f}')
        t_prev = t
        x_prev = x


def aircraft_x_array() -> np.ndarray:
    """Takes the AIRCRAFT_ASPECTS and the camera data to create a numpy array of the aircraft position.
    """
    array = np.empty((len(AIRCRAFT_ASPECTS), 4), dtype=np.float64)
    for f, frame in enumerate(sorted(AIRCRAFT_ASPECTS)):
        # Compute mid point of span
        mid_span = map_funcs.mid_point(
            AIRCRAFT_ASPECTS[frame].left_tip,
            AIRCRAFT_ASPECTS[frame].right_tip,
        )
        array[f, 0] = frame_to_time(frame)
        for b, brg_deg in enumerate(
                (
                    bearing_x_degrees(mid_span.x),
                    bearing_x_degrees(
                        mid_span.x - AIRCRAFT_ASPECTS_ERROR_PIXELS, +PX_PER_DEGREE_ERROR
                    ) - CAMERA_BEARING_ERROR,
                    bearing_x_degrees(
                        mid_span.x + AIRCRAFT_ASPECTS_ERROR_PIXELS, -PX_PER_DEGREE_ERROR
                    ) + CAMERA_BEARING_ERROR,)
        ):
            # Compute x, y relative to runway
            theta_deg = brg_deg - google_earth.RUNWAY_HEADING_DEG
            x = CAMERA_POSITION_XY.x - CAMERA_POSITION_XY.y * math.tan(math.radians(90 - theta_deg))
            array[f, b + 1] = x
    return array


# def get_x_fits() -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
#     """Returns a fit of the x position and plus, minus."""
#     array = aircraft_bearings_and_x()
#     # print(array)
#     # print(curve_fit(polynomial.polynomial_3, array[:, 0], array[:, 1])[0])
#     # print(curve_fit(polynomial.polynomial_3, array[:, 0], array[:, 2])[0])
#     # print(curve_fit(polynomial.polynomial_3, array[:, 0], array[:, 3])[0])
#     x_fits = (
#         curve_fit(polynomial.polynomial_3, array[:, 0], array[:, i])[0]
#         for i in range(1, 4)
#     )
#     return x_fits


def get_v_array() -> np.ndarray:
    """Returns a fit of the speed and plus, minus."""
    x_array = aircraft_x_array()
    x_fits = list(
        curve_fit(polynomial.polynomial_3, x_array[:, 0], x_array[:, i])[0]
        for i in range(1, 4)
    )
    v_array = np.empty_like(x_array)
    v_array[:, 0] = x_array[:, 0]
    # print(x_fits)
    for row in range(len(x_array)):
        v_array[row, 1] = polynomial.polynomial_3_differential(v_array[row, 0], *x_fits[0])
        v_array[row, 2] = polynomial.polynomial_3_differential(v_array[row, 0], *x_fits[1])
        v_array[row, 3] = polynomial.polynomial_3_differential(v_array[row, 0], *x_fits[2])
    return v_array


def main() -> int:
    print('CAMERA_POSITION_XY', CAMERA_POSITION_XY)
    print(
        'Helicopter transit time',
        (
            FRAME_EVENTS_STR_KEY['Helicopter transit'] - FRAME_EVENTS_STR_KEY['First appearance']
        ) / FRAME_RATE
    )
    print_pixels_per_degree_data()
    print_camera_axis_bearing_data()
    print(f'Focal length: {focal_length():.2f}')
    # print_aspects()
    print_aircraft_bearings_and_ranges()
    print_aircraft_bearings_and_x()
    print('X +/- over time')
    print(aircraft_x_array())
    # get_x_fits()
    print('V derived from differential of x')
    print(get_v_array())
    return 0


if __name__ == '__main__':
    sys.exit(main())
