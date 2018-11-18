import collections
import math

from analysis import video_data
from analysis import video_utils

# TODO: Merge this with video_data.XY
PosXY = collections.namedtuple('PosXY', 'x, y')

# Open Street Map file that we have created, and the runway positions in pixels.
OSM_SVG_FILENAME = '../plots/OpenStreetmap_SBKP_01.svg'
RUNWAY_START = PosXY(342, 150)
RUNWAY_END = PosXY(839.75, 537.25)
X_DATUM_T0_TO_RUNWAY_END = 2058.4

# Derived constants
X_DATUM_T0_TO_RUNWAY_START = X_DATUM_T0_TO_RUNWAY_END - video_data.RUNWAY_LEN_M
RUNWAY_LEN_PX = math.sqrt((RUNWAY_END.x - RUNWAY_START.x) ** 2 + (RUNWAY_END.y - RUNWAY_START.y) ** 2)
METRE_PER_PIXEL = video_data.RUNWAY_LEN_M / RUNWAY_LEN_PX  # m / pixel
RUNWAY_DIRECTION = math.atan2(RUNWAY_END.y - RUNWAY_START.y, RUNWAY_END.x - RUNWAY_START.x)

EXTRAPOLATED_RANGE = range(-40, 40)
#: +/- 10 knots
GROUND_SPEED_OFFSETS = (
    video_utils.knots_to_m_p_s(-10.0),
    0.0,
    video_utils.knots_to_m_p_s(10.0),
)
# Bearing constants
OBSERVER_XY_IGNORE_N_FIRST_BEARINGS = 5
OBSERVER_XY_MINIMUM_BASELINE = 1250.0 # 250.0
OBSERVER_XY_TIME_RANGE = (0.0, 0.0)
# OBSERVER_XY_TIME_RANGE = (0.0, video_data.TIME_VIDEO_NOSEWHEEL_OFF.time)
# OBSERVER_XY_TIME_RANGE = (video_data.TIME_VIDEO_NOSEWHEEL_OFF.time, video_data.TIME_VIDEO_END.time + 1)




# X_AT_VIDEO_START = video_data.RUNWAY_LEN_M - X_DATUM_T0_TO_RUNWAY_END
def distance_m_to_pixels(d: float) -> float:
    """
    Takes an distance in metres and returns the distance in pixels.
    """
    runway_px_len = math.sqrt(
        (RUNWAY_END.x - RUNWAY_START.x) ** 2
        +
        (RUNWAY_END.y - RUNWAY_START.y) ** 2
    )
    m_per_pixel = video_data.RUNWAY_LEN_M / runway_px_len # m / pixel
    return d / m_per_pixel


def position_m_to_pixels(pos: PosXY) -> PosXY:
    """
    Takes an x, y position in metres and converts them to pixel position on the SVG diagram.
    The datum of x is the start of video.
    The datum of y is the centerline of the runway.
    """
    # x_px = (pos.x + X_AT_VIDEO_START) / METRE_PER_PIXEL
    x_px = pos.x / METRE_PER_PIXEL
    y_px = pos.y / METRE_PER_PIXEL
    x_px_svg = x_px * math.cos(RUNWAY_DIRECTION) - y_px * math.sin(RUNWAY_DIRECTION)
    y_px_svg = x_px * math.sin(RUNWAY_DIRECTION) + y_px * math.cos(RUNWAY_DIRECTION)
    return PosXY(x_px_svg + RUNWAY_START.x, y_px_svg + RUNWAY_START.y)