import math
import typing

import map_funcs
from data.antonov_an24 import ANTONOV_AN_24_SPAN, ANTONOV_AN_24_LENGTH, ANTONOV_AN_24_HEIGHT

#------------ Security Camera as Video B ------------
URL = 'https://youtu.be/BQ8ujmRhLH0'

VIDEO_FILE = 'video_images/AirportCamera.mp4'
FRAMES_DIRECTORY = 'video_images/AirportCamera_frames'
FRAME_RATE = 25
FRAME_FIRST_APPEARANCE = 36
FRAME_HELICOPTER_TRANSIT = 86


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

print('Helicopter transit time', (
        FRAME_HELICOPTER_TRANSIT - FRAME_FIRST_APPEARANCE) / FRAME_RATE)

# Rough estimate of distance and video time when the aircraft transits the helicopter.
# Transit position is Point(2262, 1170)
# Runway start is (3210, 103)
# Runway end is (1066.5, 2508.0)
# Runway length is math.sqrt((3210-1066.5)**2 + (2508-103)**2)) == 3221.6


# The key is the frame number

print('Aspects:')
for k in sorted(AIRCRAFT_ASPECTS.keys()):
    print(f'{k:3d} aspect={aspect :5.3f} x: {mid_point.x:6.2f} y: {mid_point.y:6.2f}')


print('Aspects from tail height:')
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