"""
Data from video B, a fixed camera.
"""
import itertools
import math
import sys
import typing

import map_funcs
from common import structs
from data import aircraft
from data.aircraft import ANTONOV_AN_24_SPAN, ANTONOV_AN_24_LENGTH, ANTONOV_AN_24_HEIGHT
import data.google_earth

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
    data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['camera_B']
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
        k in data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
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
    ge_measurements = data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
    m_per_px = data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
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
    ge_measurements = data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
    m_per_px = data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
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
    aspect = helicopter_bearing - data.google_earth.RUNWAY_HEADING_DEG
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
    return px_per_degree_mean, px_per_degree_error


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
    ge_measurements = data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']
    m_per_px = data.google_earth.GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
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
    return camera_bearing_mean, camera_bearing_error


CAMERA_BEARING, CAMERA_BEARING_ERROR = camera_axis_bearing()


def bearing_x_degrees(p: int) -> float:
    """Returns the bearing of the x pixel in degrees."""
    db = (p - VIDEO_WIDTH / 2.0) / PX_PER_DEGREE
    return CAMERA_BEARING + db


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


def main() -> int:
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
    return 0


if __name__ == '__main__':
    sys.exit(main())
