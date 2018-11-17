"""
Thread: https://www.pprune.org/rumours-news/613321-air-x-340-brasil.html

Videos:
https://www.youtube.com/watch?v=Y6PNFzVvlWo
https://youtu.be/Y6PNFzVvlWo
https://youtu.be/XbWaXdA5jY0

Other notes (times are mm:ss::ff @ 30 f.p.s)

Nose wheel off at around 00:17:27
Main gear off at around 00:25:19
Nose over the end of the asphalt at around 00:27:24
Last usable frame 00:35:20

Aircraft:
---------
Identified as a A340-300 9H-BIG: https://www.youtube.com/watch?v=XbWaXdA5jY0&feature=youtu.be
Flight radar: https://www.flightradar24.com/data/aircraft/9h-big
Plane spotters: https://www.planespotters.net/airframe/Airbus/A340/9H-BIG-AIR-X-Charter/RJgIaj
Wikipedia on A340 (with plan drawings): https://en.wikipedia.org/wiki/Airbus_A340

Operator:
https://en.wikipedia.org/wiki/AirX_Charter


Airport:
--------
https://en.wikipedia.org/wiki/Viracopos_International_Airport
Runway: 15/33 3,240m 10,630ft

From the presence of the dual carriageway and WikiMedia maps it is runway 15:
https://tools.wmflabs.org/geohack/geohack.php?pagename=Viracopos_International_Airport&params=23_00_25_S_047_08_04_W_region:BR_type:airport
Open street map:
https://www.openstreetmap.org/?mlat=-23.006944&mlon=-47.134444&zoom=14#map=15/-23.0116/-47.1248

Other:
Google street view looking towards probable location of the observer:
https://www.google.com/maps/@-23.0148861,-47.1181774,3a,75y,270h,90t/data=!3m6!1e1!3m4!1ss_1SN7S8JIhY2Xxdt04GCg!2e0!7i13312!8i6656


"""

import collections
import enum
import itertools
import math
import pprint
import typing

import numpy as np

from analysis import video_utils


class ErrorDirection(enum.Enum):
    MIN = -1 # Use the error terms to make the value as small as possible
    MID = 0 # Use no error term
    MAX = 1 # Use the error terms to make the value as large as possible

    def __neg__(self):
        return ErrorDirection(ErrorDirection.MIN)


    def __pos__(self):
        return ErrorDirection(ErrorDirection.MAX)


    def __abs__(self):
        return ErrorDirection(ErrorDirection.MAX)


    def __invert__(self):
        if self.value == ErrorDirection.MIN:
            return ErrorDirection(ErrorDirection.MAX)
        elif self.value == ErrorDirection.MAX:
            return ErrorDirection(ErrorDirection.MIN)
        return ErrorDirection(ErrorDirection.MID)


FRAMES_PER_SECOND = 30
# +/- error in time measurements
ERROR_TIMESTAMP_FRAMES = 5.0
ERROR_TIMESTAMP = ERROR_TIMESTAMP_FRAMES / FRAMES_PER_SECOND

# Nose to tailcone in metres
# Reference: https://en.wikipedia.org/wiki/Airbus_A340 A340-300
AIRCRAFT_LENGTH = 63.6
# TODO: Check this
AIRCRAFT_SPAN = 60.3


def apply_min_mid_max_error(func: typing.Callable,
                            t: float,
                            min_mid_max: ErrorDirection,
                            err: float) -> float:
    """If min_max_t is zero this returns the function called with t.
    If min_max_t non zero this applies worst time and measurement error"""
    if min_mid_max == ErrorDirection.MID:
        return func(t)
    assert err >= 0
    if min_mid_max == ErrorDirection.MAX:
        if func(t + ERROR_TIMESTAMP) > func(t):
            return func(t + ERROR_TIMESTAMP) + err
        else:
            return func(t - ERROR_TIMESTAMP) + err
    assert min_mid_max == ErrorDirection.MIN
    if func(t + ERROR_TIMESTAMP) < func(t):
        return func(t + ERROR_TIMESTAMP) - err
    else:
        return func(t - ERROR_TIMESTAMP) - err


class VideoTime(collections.namedtuple('VideoTime', 'min, sec, frame')):
    __slots__ = ()

    def __new__(cls, *args):
        if len(args) != 3:
            raise ValueError('Need 3 arguments not {:d}'.format(len(args)))
        if not 0 <= args[0] < 60:
            raise ValueError('Minutes must be 0 <= minutes < 60 not {}'.format(args[0]))
        if not 0 <= args[1] < 60:
            raise ValueError('Seconds must be 0 <= seconds < 60 not {}'.format(args[1]))
        if not 0 <= args[2] < 30:
            raise ValueError('Frame must be 0 <= frame < 30 not {}'.format(args[2]))
        return super().__new__(cls, *args)

    @property
    def time(self):
        # Frame range is 0 <= f < 30
        return self.min * 60.0 + self.sec + self.frame / 30.0

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time

    def __format__(self, format_spec):
        if format_spec == '':
            format_spec = '02d'
        return 'VideoTime({min:{format_spec}}:{sec:{format_spec}}:{frame:{format_spec}})'.format(
            min=self.min, sec=self.sec, frame=self.frame, format_spec=format_spec
        )


TIME_VIDEO_BEGIN = VideoTime(0, 0, 0)
TIME_VIDEO_END = VideoTime(0, 35, 20)
TIME_VIDEO_MAX_AS_INT = int(TIME_VIDEO_END.time + 1)

# These times from GoPro editing software do not agree at all with the frame snaps
# Quicktime frame 14 is the frame that ticks the counter over
# GoPro frame numbers are 0 <= f < 30
# ffmpeg - every second image 1 is identical to image 2
# ffmpeg - every frame image 1 is identical to image 2
#
# Some comparisons:
#
# Quicktime     GoPro       ffmpeg - every frame    ffmpeg - every second
# ---------     -----       --------------------    ---------------------
# 00:01:00      00:00:14     16                     between 2 and 3
# 00:04:00      00:03:14    106                     between 5 and 6
# 00:09:00      00:08:14    256                     between 10 and 11
# 00:18:00      00:17:14    526                     around 20
# N/A           00:17:27    539                     Just before 20
# N/A           00:25:19    771                     28
# N/A           00:27:24    835                     Just before 30
# Last usable frame
# 00:34:00      00:33:18    1010                    35 to 36
#
# So ffmpeg - every frame is GoPro -2
# ffmpeg - frame 1 is identical to frame 2 (like per second it is duplicating the first frame)
# ffmped numbering starts from 1 so there is an off-by-2 error. t=0 is ffmpeg named 2.
#
# Let's take the GoPro application as the source of truth, then with ffmpeg all frames - 2 as equivalent.


def video_frame_to_time(video_frame: int) -> VideoTime:
    """Converts video frame number to time."""
    return VideoTime(
        video_frame // FRAMES_PER_SECOND // 60,
        (video_frame // FRAMES_PER_SECOND) % 60,
        video_frame %  FRAMES_PER_SECOND,
    )


def video_time_to_ffmepeg_time(vt: VideoTime) -> VideoTime:
    """Converts video time to a ffmpeg frame number."""
    video_frame = int(vt.time * FRAMES_PER_SECOND + 2)
    return video_frame_to_time(video_frame)


def video_time_to_ffmpeg_name(vt: VideoTime) -> str:
    """Converts video time to a ffmpeg filename."""
    return 'image{:06d}.png'.format(int(vt.time * FRAMES_PER_SECOND + 2))


def ffmpeg_time_to_video_time(vt: VideoTime) -> VideoTime:
    """Converts ffmpeg frame number to video time."""
    video_frame = int(vt.time * FRAMES_PER_SECOND - 2)
    return video_frame_to_time(video_frame)


def ffmpeg_name_to_video_time(name: str) -> VideoTime:
    """Converts ffmpeg filename video time."""
    frame = int(name[len('image'):len('image')+6])
    return video_frame_to_time(frame - 2)


# Other events
#: Nose wheel off at around 00:17:27
TIME_VIDEO_NOSEWHEEL_OFF = VideoTime(0, 17, 27)
#: Main gear off at around 00:25:19
TIME_VIDEO_MAINWHEEL_OFF = VideoTime(0, 25, 19)
#: Nose over the end of the asphalt at around 00:27:24 (27.8 seconds)
TIME_VIDEO_END_ASPHALT = VideoTime(0, 27, 24)

# Other data
#: Runway length in metres
RUNWAY_LEN_M = 3240

#: +/- error in aspect measurements in degrees
_ERROR_ASPECT = 5.0


class AircraftAspect(collections.namedtuple('AircraftAspect', 'video_time, angle, note')):

    @property
    def error(self) -> float:
        return _ERROR_ASPECT

    def __eq__(self, other):
        return self.video_time.time == other.video_time.time

    def __lt__(self, other):
        return self.video_time.time < other.video_time.time


AIRCRAFT_ASPECTS: typing.Tuple[AircraftAspect] = (
    # Increase the first two values? They seem to be outliers.
    AircraftAspect(VideoTime(0, 1, 5), 360 - 18.8, 'Nose to LH front of number 3.'),
    AircraftAspect(VideoTime(0, 4, 1), 360 - 21.5, 'Nose to front centre of number 3.'),
    AircraftAspect(VideoTime(0, 6, 24), 360 - 23.7, 'Nose to RH front of number 3.'),
    AircraftAspect(VideoTime(0, 15, 15), 360 - 29.4, 'Number 1 to tailfin tip.'),
    # Original measurements at same point in time:
    # AircraftAspect(VideoTime(0, 16, 9), 360 - 32.9, 'Nose to front centre number 4.'),
    # AircraftAspect(VideoTime(0, 16, 9), 360 - 32.0, 'Front right number 1 to left tail L/E root.'),
    # Replace by average:
    AircraftAspect(
        VideoTime(0, 16, 9), 360 - (32.9 + 32.0) / 2,
        'Average of:Nose to front centre number 4 and Front right number 1 to left tail L/E root.'),
    AircraftAspect(VideoTime(0, 17, 23), 360 - 36.5, 'Right windscreen to right wing tip.'),
    AircraftAspect(VideoTime(0, 21, 18), 360 - 44.5, 'Left wing tip to left tail tip.'),
    AircraftAspect(VideoTime(0, 23, 28), 360 - 55.3, 'Left wing tip to tail fin tip.'),
    AircraftAspect(VideoTime(0, 25, 19), 360 - 65.1, 'Left wing tip to left tail L/E root.'),
    # TODO: This measurement looks wrong, more like around 00:32:00
    # AircraftAspect(VideoTime(0, 29, 21), 360 - 90.0, 'Engines, U/C line up.'),
    AircraftAspect(VideoTime(0, 32, 0), 360 - 90.0, 'Engines, U/C line up.'),
    AircraftAspect(VideoTime(0, 32, 18), 360 - 105.8, 'Left wing tip to end of row of windows.'),
)


#: +/- error in aspect measurements from wing tips in pixels.
#: This is added to length/span to compute the error
_ERROR_ASPECT_FROM_WING_TIPS_PX = 18


# Measuring aspect from the relative separation of the wing tips compared to the aircraft length
# span, length are in pixels
# span is +ve if observer is ahead of the aircraft
# length is +ve if the observer is to the right of the observer axis.
# TODO: Write a test for the error calculation.
class AircraftAspectWingTips(collections.namedtuple('AircraftAspect', 'video_time, span, length, note')):

    @property
    def angle(self) -> float:
        """Return the aspect in degrees in the range 0 <= aspect < 360"""
        return self._aspect(self.length, self.span)

    def _aspect(self, length: float, span: float) -> float:
        aspect = math.degrees(math.atan2(length / AIRCRAFT_LENGTH, span / AIRCRAFT_SPAN))
        return aspect % 360

    @property
    def error(self) -> float:
        aspect = self.angle
        errors = [
            self._aspect(
                self.length + _ERROR_ASPECT_FROM_WING_TIPS_PX,
                self.span + _ERROR_ASPECT_FROM_WING_TIPS_PX,
            ),
            self._aspect(
                self.length - _ERROR_ASPECT_FROM_WING_TIPS_PX,
                self.span - _ERROR_ASPECT_FROM_WING_TIPS_PX,
            ),
            self._aspect(
                self.length + _ERROR_ASPECT_FROM_WING_TIPS_PX,
                self.span - _ERROR_ASPECT_FROM_WING_TIPS_PX,
            ),
            self._aspect(
                self.length - _ERROR_ASPECT_FROM_WING_TIPS_PX,
                self.span + _ERROR_ASPECT_FROM_WING_TIPS_PX,
            ),
        ]
        # WARN: Might be bogus near 0 degrees
        diffs = [abs(e - aspect) for e in errors]
        result = max(diffs)
        return result

    def __eq__(self, other):
        return self.video_time.time == other.video_time.time

    def __lt__(self, other):
        return self.video_time.time < other.video_time.time


AIRCRAFT_ASPECTS_FROM_WING_TIPS_VIDEO_FRAME_WIDTH = 1280
AIRCRAFT_ASPECTS_FROM_WING_TIPS_VIDEO_FRAME_HEIGHT = 720

AIRCRAFT_ASPECTS_FROM_WING_TIPS: typing.Tuple[AircraftAspectWingTips] = (
    # Measured by selecting tip to tip and noting width and height of selection in pixels
    # and then computing the diagonal.
    # Values are (span, length) in pixels.
    # If observer is to the right of the aircraft axis length is +ve, to the left -ve.
    # If observer is ahead of the aircraft lateral axis the span is +ve, behind -ve.
    #
    # Data is taken from every frame extracted by ffmpeg.
    # Where pitch is present the image is rotated so that the fuselage is level
    # before measuring tip-to-tip and nose-to-tail. Tip-to-tip is the maximum span
    # of the trailing edge of the winglets.
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000023.png'), 735, -257,
                           'Tail somewhat obscured, top of fin used'),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000046.png'), 746, -267, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000082.png'), 767, -281, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000092.png'), 775, -289, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000122.png'), 787, -309, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000152.png'), 807, -329, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000182.png'), 825, -356, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000205.png'), 845, -371, 'Nose obscured in image 212'),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000242.png'), 873, -403, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000272.png'), 897, -420, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000294.png'), 921, -439, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000362.png'), 593, -313, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000422.png'), 643, -379, ''),
    # t=16
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000482.png'), 683, -455, ''),
    # t=18
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000542.png'), 719, -557, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000564.png'), 729, -599, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000571.png'), 733, -611, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000811.png'), 283, -883, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000821.png'), 263, -931, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000831.png'), 257, -953, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000846.png'), 207, -979, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000856.png'), 177, -997, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000866.png'), 141, -1009, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000901.png'), 3, -751, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000911.png'), -28, -767, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000921.png'), -55, -765, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000931.png'), -81, -759, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000941.png'), -107, -753, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000951.png'), -133, -743, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000961.png'), -157, -741, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000971.png'), -219, -889, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000980.png'), -241, -879, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image000991.png'), -269, -861, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image001001.png'), -293, -839, ''),
    AircraftAspectWingTips(ffmpeg_name_to_video_time('image001010.png'), -313, -819, 'Last usable frame.'),
)

AircraftPitch = collections.namedtuple('AircraftPitch', 'video_time, angle, note')

AIRCRAFT_PITCHES = (
    AircraftPitch(VideoTime(0, 0, 0), -2.9, 'Start of video'),
    AircraftPitch(VideoTime(0, 18, 0), -1.5, 'Nose wheel off.'),
    AircraftPitch(VideoTime(0, 19, 0), 360.0 - 359.2, 'Nose wheel off.'),
    AircraftPitch(VideoTime(0, 19, 15), 360.0 - 358.4, ''),
    AircraftPitch(VideoTime(0, 20, 14), 360.0 - 357.3, ''),
    AircraftPitch(VideoTime(0, 22, 0), 360.0 - 355.6, ''),
    AircraftPitch(VideoTime(0, 23, 0), 360.0 - 354.3, ''),
    AircraftPitch(VideoTime(0, 24, 0), 360.0 - 353.8, ''),
    AircraftPitch(VideoTime(0, 25, 0), 360.0 - 353.9, 'Main wheels coming off'),
    AircraftPitch(VideoTime(0, 26, 0), 360.0 - 353.1, ''),
    AircraftPitch(VideoTime(0, 27, 0), 360.0 - 353.3, ''),
    AircraftPitch(VideoTime(0, 28, 0), 360.0 - 353.6, ''),
    AircraftPitch(VideoTime(0, 29, 0), 360.0 - 353.3, ''),
    AircraftPitch(VideoTime(0, 30, 0), 360.0 - 351.6, ''),
    AircraftPitch(VideoTime(0, 31, 0), 360.0 - 350.5, ''),
    AircraftPitch(VideoTime(0, 32, 0), 360.0 - 350.6, ''),
    AircraftPitch(VideoTime(0, 33, 20), 360.0 - 350.6, 'Last usable frame.'),
)

# +/- error in pitch measurements in degrees
ERROR_PITCH = 1.0


class AircraftTransit(collections.namedtuple('AircraftTransit', 'video_from, video_to, note')):

    @property
    def time(self):
        """Time in seconds of mid point."""
        return (self.video_to.time + self.video_from.time) / 2.0

    @property
    def dt(self):
        """Delta time in seconds."""
        return self.video_to.time - self.video_from.time

    @property
    def start(self) -> str:
        """Start time as mm:ss:ff string."""
        mins = int(self.video_from.time) // 60
        secs = int(self.video_from.time) - mins * 60
        frms = int((FRAMES_PER_SECOND * self.video_from.time) % FRAMES_PER_SECOND)
        return '{:02d}:{:02d}:{:02d}'.format(mins, secs, frms)


# Nose to tailcone
AIRCRAFT_TRANSITS = (
    AircraftTransit(VideoTime(0, 0, 20), VideoTime(0, 1, 23), 'Near lamp post 1.'),
    AircraftTransit(VideoTime(0, 1, 27), VideoTime(0, 2, 29), 'Far floodlight number 1.'),
    AircraftTransit(VideoTime(0, 2, 11), VideoTime(0, 3, 13), 'Far floodlight number 2.'),
    AircraftTransit(VideoTime(0, 2, 25), VideoTime(0, 3, 27), 'Far floodlight number 3.'),
    AircraftTransit(VideoTime(0, 3, 9), VideoTime(0, 4, 10), 'Far floodlight number 4.'),
    AircraftTransit(VideoTime(0, 3, 23), VideoTime(0, 4, 24), 'Far floodlight number 5.'),
    AircraftTransit(VideoTime(0, 4, 7), VideoTime(0, 5, 7), 'Far floodlight number 6.'),
    AircraftTransit(VideoTime(0, 4, 13), VideoTime(0, 5, 14), 'Near lamp post 2.'),
    AircraftTransit(VideoTime(0, 4, 20), VideoTime(0, 5, 20), 'Near lamp post 3.'),
    AircraftTransit(VideoTime(0, 5, 16), VideoTime(0, 6, 16), 'Near lamp post 4.'),
    AircraftTransit(VideoTime(0, 6, 12), VideoTime(0, 7, 11), 'Far comms tower number 1.'),
    AircraftTransit(VideoTime(0, 7, 24), VideoTime(0, 8, 22), 'Far comms tower number 2.'),
    AircraftTransit(VideoTime(0, 8, 14), VideoTime(0, 9, 11), 'Far comms tower number 3.'),
    AircraftTransit(VideoTime(0, 9, 3), VideoTime(0, 10, 0), 'Far comms tower number 4.'),
    AircraftTransit(VideoTime(0, 9, 11), VideoTime(0, 10, 8), 'Near lamp post number 5.'),
    AircraftTransit(VideoTime(0, 9, 23), VideoTime(0, 10, 20), 'Far comms tower number 5.'),
    AircraftTransit(VideoTime(0, 10, 3), VideoTime(0, 11, 0), 'Far floodlight number 7.'),
    AircraftTransit(VideoTime(0, 10, 8), VideoTime(0, 11, 5), 'Near lamp post number 6.'),
    AircraftTransit(VideoTime(0, 10, 12), VideoTime(0, 11, 9), 'Far comms tower number 6.'),
    AircraftTransit(VideoTime(0, 11, 2), VideoTime(0, 11, 29), 'Far comms tower number 7.'),
    AircraftTransit(VideoTime(0, 11, 19), VideoTime(0, 12, 15), 'Far comms tower number 8.'),
    AircraftTransit(VideoTime(0, 12, 0), VideoTime(0, 12, 26), 'Far comms tower number 9.'),
    AircraftTransit(VideoTime(0, 12, 19), VideoTime(0, 13, 16), 'Far comms tower number 10.'),
    AircraftTransit(VideoTime(0, 13, 1), VideoTime(0, 13, 27), 'Left edge of distant building.'),
    AircraftTransit(VideoTime(0, 13, 8), VideoTime(0, 14, 4), 'Far comms tower number 11.'),
    AircraftTransit(VideoTime(0, 13, 11), VideoTime(0, 14, 6), 'Near lamp post number 7.'),
    AircraftTransit(VideoTime(0, 13, 12), VideoTime(0, 14, 8), 'Near lamp post number 8.'),
    AircraftTransit(VideoTime(0, 13, 25), VideoTime(0, 14, 21), 'Left palm tree of a pair (tail cone obscured).'),
    AircraftTransit(VideoTime(0, 14, 14), VideoTime(0, 15, 10), 'Palm tree (tail cone obscured).'),
    AircraftTransit(VideoTime(0, 15, 5), VideoTime(0, 16, 0), 'Far comms tower number 12.'),
    AircraftTransit(VideoTime(0, 15, 11), VideoTime(0, 16, 6), 'Near lamp post number 9.'),
    AircraftTransit(VideoTime(0, 15, 24), VideoTime(0, 16, 18.5), 'Near lamp post number 10.'),
    AircraftTransit(VideoTime(0, 16, 3), VideoTime(0, 16, 27), 'Far comms tower number 13.'),
    AircraftTransit(VideoTime(0, 16, 16.5), VideoTime(0, 17, 11), 'Far comms tower number 14.'),
    AircraftTransit(VideoTime(0, 16, 27), VideoTime(0, 17, 21), 'Far comms tower number 15.'),
    AircraftTransit(VideoTime(0, 17, 9), VideoTime(0, 18, 3), 'Centre of control tower (also near lamp post number 11.'),
    AircraftTransit(VideoTime(0, 18, 2), VideoTime(0, 18, 26), 'Far comms tower number 16.'),
    AircraftTransit(VideoTime(0, 18, 11), VideoTime(0, 19, 5), 'Far comms tower number 17.'),
    AircraftTransit(VideoTime(0, 19, 9), VideoTime(0, 20, 2), 'Extreme right edge of near signage #1.'),
    AircraftTransit(VideoTime(0, 19, 26.5), VideoTime(0, 20, 19), 'Extreme left edge of near signage #1.'),
    AircraftTransit(VideoTime(0, 20, 20), VideoTime(0, 21, 12.5), 'Centre of chequered control point.'),
    AircraftTransit(VideoTime(0, 21, 15), VideoTime(0, 22, 8), 'Near lamp post number 11.'),
    AircraftTransit(VideoTime(0, 21, 28), VideoTime(0, 22, 20), 'Antenna #1.'),
    AircraftTransit(VideoTime(0, 22, 6), VideoTime(0, 22, 29), 'Antenna #2.'),
    AircraftTransit(VideoTime(0, 22, 29), VideoTime(0, 23, 21.5), 'Antenna beyond chequered building.'),
    AircraftTransit(VideoTime(0, 24, 3), VideoTime(0, 24, 25), 'Right edge of far tree.'),
    AircraftTransit(VideoTime(0, 24, 14), VideoTime(0, 25, 5), 'Right edge of far treeline.'),
    AircraftTransit(VideoTime(0, 26, 6.5), VideoTime(0, 26, 28.5), 'Extreme left edge of near signage #2.'),
    AircraftTransit(VideoTime(0, 27, 20), VideoTime(0, 28, 11), 'Distant large radio tower.'),
    AircraftTransit(VideoTime(0, 28, 22), VideoTime(0, 29, 13), 'Large tower.'),
    AircraftTransit(VideoTime(0, 31, 23), VideoTime(0, 32, 13), 'Edge of cables in the foreground.'),
    AircraftTransit(VideoTime(0, 32, 2), VideoTime(0, 32, 22), 'Right edge of poll for cables in the foreground.'),
)

# Create a dict of these, useful for the transit lines below
AIRCRAFT_TRANSIT_DICT = {}
for __transit in AIRCRAFT_TRANSITS:
    assert __transit.note not in AIRCRAFT_TRANSIT_DICT, 'Duplicate: {}'.format(__transit.note)
    AIRCRAFT_TRANSIT_DICT[__transit.note] = __transit


TRANSIT_REFERENCE_LENGTH = AIRCRAFT_LENGTH

# +/- error in transit delta time measurements in seconds, say +/- 1 frames
# The transit error depends on aspect. Divide by sin(aspect) so infinite error when aspect == 0
# and 1.0 / 30 when aspect == 90 degreees.
ERROR_TRANSIT = 1.0 / 30


# Screenshots use to determine video magnification/field of view

AircraftApparentLength = collections.namedtuple('AircraftApparentLength', 'video_time, length_px')


SCREENSHOT_WIDTH = 2448
SCREENSHOT_HEIGHT = 1379


AIRCRAFT_LENGTH_IN_PIXELS = (
    AircraftApparentLength(VideoTime(0, 2, 0), 542),
    AircraftApparentLength(VideoTime(0, 3, 0), 557),
    AircraftApparentLength(VideoTime(0, 4, 0), 595),
    AircraftApparentLength(VideoTime(0, 5, 0), 627),
    AircraftApparentLength(VideoTime(0, 6, 0), 671),
    AircraftApparentLength(VideoTime(0, 7, 0), 768),
    AircraftApparentLength(VideoTime(0, 8, 0), 765),
    AircraftApparentLength(VideoTime(0, 9, 0), 797),
    AircraftApparentLength(VideoTime(0, 10, 0), 848),
    AircraftApparentLength(VideoTime(0, 11, 0), 913),
    AircraftApparentLength(VideoTime(0, 12, 0), 595),
    AircraftApparentLength(VideoTime(0, 13, 0), 666),
    AircraftApparentLength(VideoTime(0, 14, 0), 719),
    AircraftApparentLength(VideoTime(0, 15, 0), 792),
    AircraftApparentLength(VideoTime(0, 16, 0), 865),
    AircraftApparentLength(VideoTime(0, 17, 0), 959),
    AircraftApparentLength(VideoTime(0, 18, 0), 1063),
    AircraftApparentLength(VideoTime(0, 19, 0), 1180),
    AircraftApparentLength(VideoTime(0, 20, 0), 1300), # Tail obscured
    AircraftApparentLength(VideoTime(0, 21, 0), 1448), # Tail obscured
    AircraftApparentLength(VideoTime(0, 22, 0), 1631),
    AircraftApparentLength(VideoTime(0, 23, 0), 1192),
    AircraftApparentLength(VideoTime(0, 24, 0), 1313),
    AircraftApparentLength(VideoTime(0, 25, 0), 1456),
    AircraftApparentLength(VideoTime(0, 27, 0), 1738),
    AircraftApparentLength(VideoTime(0, 28, 0), 1856),
    AircraftApparentLength(VideoTime(0, 29, 0), 1934),
    AircraftApparentLength(VideoTime(0, 30, 0), 1425),
    AircraftApparentLength(VideoTime(0, 31, 0), 1437),
    AircraftApparentLength(VideoTime(0, 32, 0), 1407),
    AircraftApparentLength(VideoTime(0, 33, 0), 1633),
)


ERROR_AIRCRAFT_LENGTH_IN_PIXELS = 10


#================== Data from Google Earth ==============
# Tower positions in the open nearest 15 threshold
"""
Tower 1: https://www.google.com/maps/@-23.001859,-47.148885,59m/data=!3m1!1e3?hl=en
Tower 2: https://www.google.com/maps/@-23.002109,-47.148531,59m/data=!3m1!1e3?hl=en
Tower 3: https://www.google.com/maps/@-23.002358,-47.148179,59m/data=!3m1!1e3?hl=en
Tower 4: https://www.google.com/maps/@-23.002612,-47.147815,59m/data=!3m1!1e3?hl=en
Tower 5: https://www.google.com/maps/@-23.002856,-47.147467,59m/data=!3m1!1e3?hl=en
Tower 6: https://www.google.com/maps/@-23.003107,-47.147108,59m/data=!3m1!1e3?hl=en
"""

# Tower positions furthest to the northeast wing of terminal 1
# Adjustment to Tower 2 by -1 metre heading 150 dlat=7.8e-6 dlong=-4.5e-6:
# Was:
# Tower 8: https://www.google.com/maps/@-23.0042240,-47.1502493,59m/data=!3m1!1e3?hl=en
# Tower 8: https://www.google.com/maps/@-23.0042162,-47.1502538,59m/data=!3m1!1e3?hl=en
# Maybe .5 m more
# Tower 8: https://www.google.com/maps/@-23.0042123,-47.1502560,59m/data=!3m1!1e3?hl=en
"""
Tower 7: https://www.google.com/maps/@-23.0039523,-47.1506005,59m/data=!3m1!1e3?hl=en
# Adjustment to even tower spacing to average of 45.6 m, was:
# Tower 8: https://www.google.com/maps/@-23.0042240,-47.1502493,59m/data=!3m1!1e3?hl=en
Tower 8: https://www.google.com/maps/@-23.0042123,-47.1502560,59m/data=!3m1!1e3?hl=en
# Adjustment to even tower spacing to average of 45.6 m, was:
#Tower 9: https://www.google.com/maps/@-23.0044624,-47.1498953,59m/data=!3m1!1e3?hl=en
Tower 9: https://www.google.com/maps/@-23.0044700,-47.1499050,59m/data=!3m1!1e3?hl=en
Tower 10: https://www.google.com/maps/@-23.0047257,-47.1495659,59m/data=!3m1!1e3?hl=en
Tower 11: https://www.google.com/maps/@-23.0049800,-47.1492158,59m/data=!3m1!1e3?hl=en
Tower 12: https://www.google.com/maps/@-23.0052343,-47.1488650,59m/data=!3m1!1e3?hl=en
"""

# Tower positions furthest to the southwest wing of terminal 1
"""
Tower 13: https://www.google.com/maps/@-23.005718,-47.151876,59m/data=!3m1!1e3?hl=en
Tower 14: https://www.google.com/maps/@-23.005967,-47.151523,59m/data=!3m1!1e3?hl=en
Tower 16: https://www.google.com/maps/@-23.006215,-47.151173,59m/data=!3m1!1e3?hl=en
Tower 16: https://www.google.com/maps/@-23.006463,-47.150828,59m/data=!3m1!1e3?hl=en
Tower 17: https://www.google.com/maps/@-23.006715,-47.150475,59m/data=!3m1!1e3?hl=en
Tower 18: https://www.google.com/maps/@-23.006960,-47.150124,59m/data=!3m1!1e3?hl=en
Tower 19: https://www.google.com/maps/@-23.007207,-47.149788,59m/data=!3m1!1e3?hl=en
"""

# Lat long: 1m on earths surface is 1 / 6378.137e3 radians latitude or about 9e-6 degrees say 0.00001
# 25m is 0.00025
# Lat long: 9e-6 degrees latitude is around 1.323e-05 degrees longitude
GOOGLE_EARTH_URLS = """
# Tower positions in the open nearest 15 threshold
Tower 1: https://www.google.com/maps/@-23.001859,-47.148885,59m/data=!3m1!1e3?hl=en
Tower 2: https://www.google.com/maps/@-23.002109,-47.148531,59m/data=!3m1!1e3?hl=en
Tower 3: https://www.google.com/maps/@-23.002358,-47.148179,59m/data=!3m1!1e3?hl=en
Tower 4: https://www.google.com/maps/@-23.002612,-47.147815,59m/data=!3m1!1e3?hl=en
Tower 5: https://www.google.com/maps/@-23.002856,-47.147467,59m/data=!3m1!1e3?hl=en
Tower 6: https://www.google.com/maps/@-23.003107,-47.147108,59m/data=!3m1!1e3?hl=en

# Tower positions furthest to the northeast wing of terminal 1
Tower 7: https://www.google.com/maps/@-23.0039523,-47.1506005,59m/data=!3m1!1e3?hl=en
# Adjustment to even tower spacing to average of 45.6 m, was:
# Tower 8: https://www.google.com/maps/@-23.0042240,-47.1502493,59m/data=!3m1!1e3?hl=en
Tower 8: https://www.google.com/maps/@-23.0042123,-47.1502560,59m/data=!3m1!1e3?hl=en
# Adjustment to even tower spacing to average of 45.6 m, was:
#Tower 9: https://www.google.com/maps/@-23.0044624,-47.1498953,59m/data=!3m1!1e3?hl=en
Tower 9: https://www.google.com/maps/@-23.0044700,-47.1499050,59m/data=!3m1!1e3?hl=en
Tower 10: https://www.google.com/maps/@-23.0047257,-47.1495659,59m/data=!3m1!1e3?hl=en
Tower 11: https://www.google.com/maps/@-23.0049800,-47.1492158,59m/data=!3m1!1e3?hl=en
Tower 12: https://www.google.com/maps/@-23.0052343,-47.1488650,59m/data=!3m1!1e3?hl=en

# Tower positions furthest to the southwest wing of terminal 1
Tower 13: https://www.google.com/maps/@-23.005718,-47.151876,59m/data=!3m1!1e3?hl=en
Tower 14: https://www.google.com/maps/@-23.005967,-47.151523,59m/data=!3m1!1e3?hl=en
Tower 15: https://www.google.com/maps/@-23.006215,-47.151173,59m/data=!3m1!1e3?hl=en
Tower 16: https://www.google.com/maps/@-23.006463,-47.150828,59m/data=!3m1!1e3?hl=en
Tower 17: https://www.google.com/maps/@-23.006715,-47.150475,59m/data=!3m1!1e3?hl=en
Tower 18: https://www.google.com/maps/@-23.006960,-47.150124,59m/data=!3m1!1e3?hl=en
Tower 19: https://www.google.com/maps/@-23.007207,-47.149788,59m/data=!3m1!1e3?hl=en

# Runway ends
Threshold 15: https://www.google.com/maps/@-22.9985032,-47.1469772,61m/data=!3m1!1e3?hl=en
End asphalt 15: https://www.google.com/maps/@-23.0163963,-47.1219874,63m/data=!3m1!1e3?hl=en
Threshold 33: https://www.google.com/maps/@-23.015869,-47.1227499,61m/data=!3m1!1e3?hl=en


# Full transit at Tower 1 to Fence Break 1 at VideoTime(0, 2, 12)
# Fence Break 1: https://www.google.com/maps/@-23.008622,-47.127443,61m/data=!3m1!1e3?hl=en
# Move 20m north: +.00020
Fence Break 1: https://www.google.com/maps/@-23.008422,-47.127443,61m/data=!3m1!1e3?hl=en


# Simultaneous transit at VideoTime(0, 7, 17) or VideoTime(0, 7, 18) of 'Tower 8' and:
Concrete block hut: https://www.google.com/maps/@-23.008705,-47.129063,50m/data=!3m1!1e3

# Probably misidentified?
# Fedex left: https://www.google.com/maps/@-23.0154296,-47.1296299,61m/data=!3m1!1e3?hl=en
# Yes this looks more accurate
Fedex left: https://www.google.com/maps/@-23.016525,-47.127947,61m/data=!3m1!1e3?hl=en
# Fedex right: https://www.google.com/maps/@-23.0153072,-47.1298295,61m/data=!3m1!1e3?hl=en
# Yes this looks more accurate
Fedex right: https://www.google.com/maps/@-23.016425,-47.128094,61m/data=!3m1!1e3?hl=en

# Simultaneous transit at VideoTime(0, 24, 26)
# Probably misidentified?
# Trees right of Fedex: https://www.google.com/maps/@-23.0147636,-47.1303907,104m/data=!3m1!1e3
# Yes this looks more accurate
Trees right of Fedex: https://www.google.com/maps/@-23.016282,-47.128253,104m/data=!3m1!1e3
Factory interior corner: https://www.google.com/maps/@-23.0135093,-47.1203631,50m/data=!3m1!1e3

Control tower base: https://www.google.com/maps/@-23.010773,-47.145509,61m/data=!3m1!1e3?hl=en
# Simultaneous transit at VideoTime(0, 17, 22) Control tower base and Embankment inside corner, est. (-23.011606,-47.124922)
Embankment inside corner: https://www.google.com/maps/@-23.011606,-47.124922,61m/data=!3m1!1e3?hl=en

# Transit at 00:23::08
Chequer board hut: https://www.google.com/maps/@-23.0137084,-47.1237547,98m/data=!3m1!1e3

# See VideoTime(0, 26, 5) for the angle:
# VideoTime(0, 26, 17) Far factory with cream stripe on roof (-23.017518,-47.126642) and:
# Left edge of sign ALUGAM-SE Left (-23.012971,-47.117859)
# Factory cream stripe -> ALUGAM-SE Left VideoTime(0, 26, 17)
Factory cream stripe: https://www.google.com/maps/@-23.017518,-47.126642,98m/data=!3m1!1e3
ALUGAM-SE Left: https://www.google.com/maps/@-23.012971,-47.117859,98m/data=!3m1!1e3

Factory extreme left: https://www.google.com/maps/@-23.0147028,-47.120441,55m/data=!3m1!1e3

# Simultaneous transit at VideoTime(0, 28, 0)
Tall radio tower: https://www.google.com/maps/@-23.0210104,-47.1285102,97m/data=!3m1!1e3
# Alternate
# Tall radio tower: https://www.google.com/maps/@-23.020989,-47.128512,97m/data=!3m1!1e3
Second control tower: https://www.google.com/maps/@-23.0213449,-47.1261314,174m/data=!3m1!1e3
# This the corner of a building by a white hut that is just visible at 00:28:00 and in line with 'Tall radio tower'
Building corner: https://www.google.com/maps/@-23.015572,-47.120916,97m/data=!3m1!1e3
"""

# These are towers in the North West area of the airport.
# They are clearly visible in the early part of the video.
# These are organised as a variable width table of pairs of (lat, long)
GOOGLE_EARTH_TOWER_POSITIONS_LAT_LONG = (
    # These six towers are in the open to the North East of the terminal building.
    # They have a group of lights at the very top that make a distinctive butterfly shadow.
    tuple(
        [
            # video_utils.interpolate_between_two_points(-23.001859, -47.148889, -23.003105, -47.147112, i / 5.0)
            # # dy is -0.4 so tweak end positon by 2m or 2e-5 lat
            video_utils.LatLong(
                *video_utils.interpolate_between_two_points(-23.001859, -47.148889, -23.003125, -47.147132, i / 5.0)
            )
            for i in range(6)
        ]
    ),
    # These eight towers are on the North East side of the North East Wing of the terminal building.
    # They have a larger group of lights from some distance down from the top that makes a more rounded shadow.
    tuple(
        [
            # video_utils.interpolate_between_two_points(-23.003361, -47.149942, -23.005109, -47.147447, i / 7.0)
            # # dy is -0.4 so tweak end positon by 2m or 2e-5 lat
            video_utils.LatLong(
                *video_utils.interpolate_between_two_points(-23.003361, -47.149942, -23.005129, -47.147467, i / 7.0)
            )
            for i in range(8)
        ]
    ),
    # These six towers are on the South West side of the North East Wing of the terminal building.
    # They have a larger group of lights from some distance down from the top that makes a more rounded shadow.
    tuple(
        [
            video_utils.LatLong(
                *video_utils.interpolate_between_two_points(-23.003940, -47.150579, -23.005186, -47.148830, i / 5.0)
            )
            for i in range(6)
        ]
    ),
    # These seven towers are on the North East side of the South West Wing of the terminal building.
    # They have a larger group of lights from some distance down from the top that makes a more rounded shadow.
    tuple(
        [
            video_utils.LatLong(
                *video_utils.interpolate_between_two_points(-23.005717, -47.151878, -23.007212, -47.149789, i / 6.0)
            )
            for i in range(7)
        ]
    ),
    # These towers are on the South West side of the South West Wing of the terminal building.
    # They have a larger group of lights from some distance down from the top that makes a more rounded shadow.
    (
        video_utils.LatLong(-23.006378, -47.152455),
        video_utils.LatLong(-23.006875, -47.151753),
        video_utils.LatLong(-23.008431, -47.150984),
        video_utils.LatLong(-23.009074, -47.151511),
    )
)

GOOGLE_EARTH_TOWER_POSITIONS_TRANSIT_TIMES = (
    (
        VideoTime(0, 0, 0),
        VideoTime(0, 0, 0),
        VideoTime(0, 0, 0),
        VideoTime(0, 0, 0),
        VideoTime(0, 0, 0),
        VideoTime(0, 0, 0),
    ),
    (
        VideoTime(0, 6, 27),
        VideoTime(0, 7, 17), # Tower 8 in full transit with 'Concrete block hut'
        VideoTime(0, 8, 8),
        VideoTime(0, 8, 27),
        VideoTime(0, 9, 17),
        VideoTime(0, 10, 7),
        VideoTime(0, 10, 25),
        VideoTime(0, 11, 15),
        VideoTime(0, 12, 2), # Where is this one?
    ),
)

# xy is a video_utils.XY and are distances in metres from the datum (the start of runway 15)
# For writing URLs
GOOGLE_EARTH_URL_FORMAT = 'https://www.google.com/maps/@{:.7f},{:.7f},55m/data=!3m1!1e3'


# Dict of {label : (latitude, longitude), ...}
# latitude, longitude in degrees.
GOOGLE_EARTH_POSITIONS_LAT_LONG: typing.Dict[str, video_utils.LatLong] = {
    video_utils.google_earth_url_to_lat_long(line)[0] : video_utils.google_earth_url_to_lat_long(line)[1]
    for line in GOOGLE_EARTH_URLS.split('\n') if len(line.strip()) > 0 and not line.startswith('#')
}

# lat/long of x=0, y=0
GOOGLE_EARTH_DATUM_LAT_LONG = GOOGLE_EARTH_POSITIONS_LAT_LONG['Threshold 15']
# Bearing of x axis in degrees, mean of two measurements
GOOGLE_EARTH_X_AXIS = (
    video_utils.bearing_lat_long(
        GOOGLE_EARTH_DATUM_LAT_LONG,
        GOOGLE_EARTH_POSITIONS_LAT_LONG['Threshold 33'],
    )
    + video_utils.bearing_lat_long(
        GOOGLE_EARTH_DATUM_LAT_LONG,
        GOOGLE_EARTH_POSITIONS_LAT_LONG['End asphalt 15']
    )
) / 2.0


def google_earth_lat_long_to_xy(k: str) -> video_utils.XY:
    return video_utils.lat_long_to_xy(
        GOOGLE_EARTH_DATUM_LAT_LONG,
        GOOGLE_EARTH_X_AXIS,
        GOOGLE_EARTH_POSITIONS_LAT_LONG[k]
    )


# Dict of {label : (x, y), ...}
GOOGLE_EARTH_POSITIONS_XY = {
    k : google_earth_lat_long_to_xy(k) for k in GOOGLE_EARTH_POSITIONS_LAT_LONG
}

GOOGLE_EARTH_TOWER_POSITIONS_XY = tuple(
    [
        tuple(
            [
                video_utils.lat_long_to_xy(
                        GOOGLE_EARTH_DATUM_LAT_LONG,
                        GOOGLE_EARTH_X_AXIS,
                        lat_long_pos
                ) for lat_long_pos in row
            ]
        )
        for row in GOOGLE_EARTH_TOWER_POSITIONS_LAT_LONG
    ]
)


# Map transit lines to video events
GOOGE_EARTH_EVENT_TOWER_MAP = {
    'Tower 1' : 'Far floodlight number 1.',
    'Tower 2' : 'Far floodlight number 2.',
    'Tower 3' : 'Far floodlight number 3.',
    'Tower 4' : 'Far floodlight number 4.',
    'Tower 5' : 'Far floodlight number 5.',
    'Tower 6' : 'Far floodlight number 6.',
    # Second line of lighting towers
    'Tower 7' : 'Far comms tower number 1.',
    'Tower 8' : 'Far comms tower number 2.',
    'Tower 9' : 'Far comms tower number 3.',
    'Tower 10' : 'Far comms tower number 4.',
    'Tower 11' : 'Far comms tower number 5.',
    'Tower 12' : 'Far comms tower number 6.',
    # Third line of lighting towers
    'Tower 13' : 'Far comms tower number 7.',
    'Tower 14' : 'Far comms tower number 8.',
    'Tower 15' : 'Far comms tower number 9.',
    'Tower 16' : 'Far comms tower number 10.',
    'Tower 17' : 'Far comms tower number 11.',
    'Tower 18' : 'Far comms tower number 12.',
    'Tower 19' : 'Far comms tower number 13.',
}

#------------------ Google Earth transits -------------------

GOOGLE_EARTH_EVENT_TRANSIT_TIMES = {
    # These two points are in simultanous transit
    'Concrete block hut': VideoTime(0, 7, 17), # or VideoTime(0, 7, 18) of 'Tower 8'
    'Chequer board hut': VideoTime(0, 23, 8),
    'Control tower base': VideoTime(0, 17, 21),
    # These two points are in simultanous transit
    'Trees right of Fedex': VideoTime(0, 24, 26),
    'Factory interior corner': VideoTime(0, 24, 26),
    'Fedex left': VideoTime(0, 25, 10),
    'Fedex right': VideoTime(0, 25, 2),
    'Factory extreme left': VideoTime(0, 27, 6),
    'Tall radio tower': VideoTime(0, 28, 0),
    'Second control tower': VideoTime(0, 29, 2),
}


# in the direction along the runway. y is to the right of the runway.
FullTransitPoint = collections.namedtuple('FullTransitPoint', 'label, xy')
# frm (from) and to are FullTransitPoint(s)
FullTransitLine = collections.namedtuple('FullTransitLine', 'frm, to, time')

# Transit lines that are simultaneous
# TODO: Add these transit lines
# VideoTime(0, 13, 00) Light Stand (which one?) and fence break with hut (-23.010070,-47.127441)
# VideoTime(0, 16, 29) Light Stand (which one?) and embankment outside corner(-23.010615,-47.124007)


GOOGLE_EARTH_FULL_TRANSITS = (
    # Tower 1 to Fence Break 1 at VideoTime(0, 2, 12)
    FullTransitLine(
        FullTransitPoint(
            'Tower 1',
            google_earth_lat_long_to_xy('Tower 1')
        ),
        FullTransitPoint(
            'Fence Break 1',
            google_earth_lat_long_to_xy('Fence Break 1')
        ),
        VideoTime(0, 2, 12),
    ),
    # FullTransitLine(
    #     FullTransitPoint(
    #         'Tower 8',
    #         google_earth_lat_long_to_xy('Tower 8')
    #     ),
    #     FullTransitPoint(
    #         'Concrete block hut',
    #         google_earth_lat_long_to_xy('Concrete block hut')
    #     ),
    #     VideoTime(0, 7, 17),
    # ),
    # Simultaneous transit at VideoTime(0, 17, 22) Control tower base and Embankment inside corner, est. (-23.011606,-47.124922)
    FullTransitLine(
        FullTransitPoint(
            'Control tower base',
            google_earth_lat_long_to_xy('Control tower base')
        ),
        FullTransitPoint(
            'Embankment inside corner',
            google_earth_lat_long_to_xy('Embankment inside corner')
        ),
        VideoTime(0, 17, 22),
    ),
    FullTransitLine(
        FullTransitPoint(
            'Trees right of Fedex',
            google_earth_lat_long_to_xy('Trees right of Fedex')
        ),
        FullTransitPoint(
            'Factory interior corner',
            google_earth_lat_long_to_xy('Factory interior corner')
        ),
        VideoTime(0, 24, 26),
    ),
    # Factory cream stripe -> ALUGAM-SE Left VideoTime(0, 26, 17)
    FullTransitLine(
        FullTransitPoint(
            'Factory cream stripe',
            google_earth_lat_long_to_xy('Factory cream stripe')
        ),
        FullTransitPoint(
            'ALUGAM-SE Left',
            google_earth_lat_long_to_xy('ALUGAM-SE Left')
        ),
        VideoTime(0, 26, 17),
    ),
    FullTransitLine(
        FullTransitPoint(
            'Tall radio tower',
            google_earth_lat_long_to_xy('Tall radio tower')
        ),
        FullTransitPoint(
            'Building corner',
            google_earth_lat_long_to_xy('Building corner')
        ),
        VideoTime(0, 28, 0),
    ),
)


# ('Tower 8', 'Concrete block hut'),
# ('Trees right of Fedex', 'Factory interior corner'),
# ('Tall radio tower', 'Building corner'),
GOOGLE_EARTH_SIMULTANEOUS_TRANSIT_LABELS = tuple(
    [
        (v.frm.label, v.to.label) for v in GOOGLE_EARTH_FULL_TRANSITS
    ]
)


def transit_is_simultaneous(label: str) -> bool:
    """Returns True if the transit line lable belongs to a pair that are simultaneous"""
    for a, b in GOOGLE_EARTH_SIMULTANEOUS_TRANSIT_LABELS:
        if label == a or label == b:
            return True
    return False

#------------------ END: Google Earth transits -------------------

# Dictionary of {label : time, ...} where label is an entry in
# GOOGLE_EARTH_EVENT_TRANSIT_TIMES and GOOGLE_EARTH_POSITIONS_XY
GOOGLE_EARTH_EVENT_MAP = {}
GOOGLE_EARTH_EVENT_MAP.update(
    {
        k : v.time for k, v in GOOGLE_EARTH_EVENT_TRANSIT_TIMES.items()
    }
)
GOOGLE_EARTH_EVENT_MAP.update(
    {
        k : AIRCRAFT_TRANSIT_DICT[v].time for k, v in GOOGE_EARTH_EVENT_TOWER_MAP.items()
    }
)

# Time ordered tuple of (time, label) where label is an entry in GOOGLE_EARTH_POSITIONS_XY
# This is the reverse of GOOGLE_EARTH_EVENT_MAP
GOOGLE_EARTH_EVENTS = tuple(
    sorted([
        (v, k) for k, v in GOOGLE_EARTH_EVENT_MAP.items()
    ])
)


GOOGLE_EARTH_OBSERVER_POSIITON_URL = 'https://www.google.com/maps/@-23.0129344,-47.1164164,94m/data=!3m1!1e3'
GOOGLE_EARTH_OBSERVER_POSIITON = video_utils.google_earth_url_to_lat_long(
    'Observer: https://www.google.com/maps/@-23.0129344,-47.1164164,94m/data=!3m1!1e3'
)[1]

#================== END: Data from Google Earth ==============

def print_google_earth_tower_positions():
    print('GOOGLE_EARTH_TOWER_POSITIONS_XY:')
    # pprint.pprint(GOOGLE_EARTH_TOWER_POSITIONS_XY)
    for r, row in enumerate(GOOGLE_EARTH_TOWER_POSITIONS_XY):
        prev = None
        for c, col in enumerate(row):
            if prev is not None:
                print('[{:d}, {:d}]: {:10.1f}, {:10.1f} {:+10.3f}, {:+10.3f}'.format(
                    r, c, col[0], col[1], col[0] - prev[0], col[1] - prev[1]
                ))
            else:
                print('[{:d}, {:d}]: {:10.1f}, {:10.1f}'.format(r, c, *col))
            prev = col
    print()


OBSERVER_XY_START_RUNWAY = video_utils.XY(2266 + 1182, -763)


def print_transits_and_runway_distances():
    speed = 0.0
    prev = (0.0, 0.0, 0.0)
    # Google earth
    # observer_xy_start_runway = (3457.9, -655.5)
    print('Transits for observer at:', OBSERVER_XY_START_RUNWAY)
    for t, k in GOOGLE_EARTH_EVENTS:
        event_time = GOOGLE_EARTH_EVENT_MAP[k]
        # print(event, lat, lon)
        # print('lat, lon', k, lat, lon)
        x, y = video_utils.lat_long_to_xy(
            GOOGLE_EARTH_DATUM_LAT_LONG,
            GOOGLE_EARTH_X_AXIS,
            GOOGLE_EARTH_POSITIONS_LAT_LONG[k],
        )
        x, y = GOOGLE_EARTH_POSITIONS_XY[k]
        # print('x, y', k, x, y)
        # video_utils.transit_x_axis_intercept(lat, lon, X0, Y0)
        x_intercept = video_utils.transit_x_axis_intercept(x, y, *OBSERVER_XY_START_RUNWAY)
        # print('TRACE', k, event_time, prev[0])
        dt = event_time - prev[0]
        dx_on_axis = x_intercept - prev[1]
        dx = x - prev[2]
        if dt != 0.0:
            gs = video_utils.m_p_s_to_knots(dx_on_axis / dt)
        else:
            gs = 0.0
        print(
            '{:10s} t={:6.1f} dt={:6.1f} lat={:12.6f} lon={:12.6f} dlat={:10.6f} dlon={:10.6f} x={:6.1f} y={:6.1f} x_runway={:6.1f} dxaxis={:6.1f} v={:6.1f}'.format(
                '"{}"'.format(k),
                event_time, event_time - prev[0],
                GOOGLE_EARTH_POSITIONS_LAT_LONG[k].lat, GOOGLE_EARTH_POSITIONS_LAT_LONG[k].long,
                GOOGLE_EARTH_POSITIONS_LAT_LONG[k].lat - GOOGLE_EARTH_DATUM_LAT_LONG.lat,
                GOOGLE_EARTH_POSITIONS_LAT_LONG[k].long - GOOGLE_EARTH_DATUM_LAT_LONG.long,
                x, y,
                x_intercept, dx_on_axis, gs
            )
        )
        prev = (event_time, x_intercept, x)


def print_full_transits():
    for transit in GOOGLE_EARTH_FULL_TRANSITS:
        print(
            'Full transit at {} from {:8.3f} {:8.3f} "{}"->"{}"'.format(
                transit.time,
                transit.frm.xy, transit.to.xy,
                transit.frm.label, transit.to.label,
            )
        )
    print()
    crossing_x = []
    crossing_y = []
    for num, (i, j) in enumerate(itertools.combinations(range(len(GOOGLE_EARTH_FULL_TRANSITS)), 2)):
        transit1: FullTransitLine = GOOGLE_EARTH_FULL_TRANSITS[i]
        transit2: FullTransitLine = GOOGLE_EARTH_FULL_TRANSITS[j]
        crossing = video_utils.intersect_two_lines(
            transit1.frm.xy, transit1.to.xy, transit2.frm.xy, transit2.to.xy,
        )
        crossing_x.append(crossing.x)
        crossing_y.append(crossing.y)
        print(
            '[{:2d}] Full transit crossing {:8.3f} "{}"->"{}" and  "{}"->"{}"'.format(
                num,
                crossing,
                transit1.frm.label, transit1.to.label,
                transit2.frm.label, transit2.to.label,
            )
        )
    print(
        'X: min={:8.3f} mean={:8.3f} max={:8.3f} range={:8.3f}'.format(
            min(crossing_x), sum(crossing_x) / len(crossing_x), max(crossing_x), max(crossing_x) - min(crossing_x),
        )
    )
    print(
        'Y: min={:8.3f} mean={:8.3f} max={:8.3f} range={:8.3f}'.format(
            min(crossing_y), sum(crossing_y) / len(crossing_y), max(crossing_y), max(crossing_y) - min(crossing_y),
        )
    )


if __name__ == '__main__':
    # print('Aircraft pitch:')
    # for p in AIRCRAFT_PITCHES:
    #     print('{:8.3f} {:8.3f}'.format(p.video_time.time, p.angle))
    # print('Aspect:')
    # for p in AIRCRAFT_ASPECTS:
    #     print('{:8.3f} {:8.1f}'.format(p.video_time.time, p.angle))
    # print('Aspect from span:')
    # for p in AIRCRAFT_ASPECTS_FROM_WING_TIPS:
    #     print('{:8.3f} {:8.1f}'.format(p.video_time.time, p.angle))
    print('GOOGLE_EARTH_DATUM', GOOGLE_EARTH_DATUM_LAT_LONG)
    print('GOOGLE_EARTH_X_AXIS', GOOGLE_EARTH_X_AXIS)

    # print('FEDEX_BUILDING_WIDTH', FEDEX_BUILDING_WIDTH)
    # print('FEDEX_BUILDING_BEARING_RIGHT_LEFT', FEDEX_BUILDING_BEARING_RIGHT_LEFT)
    # print('FEDEX_OFFSET_POSITION', FEDEX_OFFSET_POSITION)
    # print('FEDEX_BEARING_TO_FACTORY_INTERIOR_CORNER', FEDEX_BEARING_TO_FACTORY_INTERIOR_CORNER)
    # y_obs = -763
    # print('fedex_x_from_y({})'.format(y_obs), fedex_x_from_y(y_obs))
    # 3276.2
    # Est. is 2298 + 1182 = 3480
    # Hmm. 200m error.

    # pprint.pprint(GOOGLE_EARTH_POSITIONS_XY)
    # pprint.pprint(GOOGLE_EARTH_EVENT_MAP)
    # pprint.pprint(GOOGLE_EARTH_EVENTS)
    # print('GOOGLE_EARTH_TOWER_POSITIONS_LAT_LONG:')
    # # pprint.pprint(GOOGLE_EARTH_TOWER_POSITIONS_LAT_LONG)
    # for r, row in enumerate(GOOGLE_EARTH_TOWER_POSITIONS_LAT_LONG):
    #     for c, col in enumerate(row):
    #         print('[{:d}, {:d}]: {:10.6f}, {:10.6f}'.format(r, c, *col))

    # print_google_earth_tower_positions()
    # print_transits_and_runway_distances()


    # Full Transits
    # for a, b in GOOGLE_EARTH_SIMULTANEOUS_TRANSIT_LABELS:
    #     print('Full transit from {:8.3f} {:8.3f} "{}"->"{}"'.format(
    #         GOOGLE_EARTH_POSITIONS_XY[a],
    #         GOOGLE_EARTH_POSITIONS_XY[b],
    #         a, b)
    #     )
    print_full_transits()
    print()

    # Observer
    ge_obs_xy = video_utils.lat_long_to_xy(
        GOOGLE_EARTH_DATUM_LAT_LONG,
        GOOGLE_EARTH_X_AXIS,
        GOOGLE_EARTH_OBSERVER_POSIITON,
    )
    print('Observer from bearings    : {:8.1f}'.format(OBSERVER_XY_START_RUNWAY))
    print('Observer from google earth: {:8.1f}'.format(ge_obs_xy))
    print('      Diff (bearings - ge): x={:6.1f} y={:6.1f}'.format(
        OBSERVER_XY_START_RUNWAY.x - ge_obs_xy.x,
        OBSERVER_XY_START_RUNWAY.y - ge_obs_xy.y))

    # TODO: Fix x/y to lat/long
    ge_obs_lat_long = video_utils.xy_to_lat_long(
        GOOGLE_EARTH_DATUM_LAT_LONG,
        GOOGLE_EARTH_X_AXIS,
        OBSERVER_XY_START_RUNWAY,
    )
    print('Google earth URL from x={:6.1f} y={:6.1f}'.format(*OBSERVER_XY_START_RUNWAY))
    print(GOOGLE_EARTH_URL_FORMAT.format(*ge_obs_lat_long))
    ge_obs_lat_long = video_utils.xy_to_lat_long(
        GOOGLE_EARTH_DATUM_LAT_LONG,
        GOOGLE_EARTH_X_AXIS,
        ge_obs_xy,
    )
    print('Google earth URL from {}'.format(ge_obs_xy))
    print(GOOGLE_EARTH_URL_FORMAT.format(*ge_obs_lat_long))
