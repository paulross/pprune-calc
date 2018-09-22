"""
Thread: https://www.pprune.org/rumours-news/613321-air-x-340-brasil.html

Videos:
https://youtu.be/Y6PNFzVvlWo
https://youtu.be/XbWaXdA5jY0

Other notes (times are mm:ss::ff @ 30 f.p.s)

Nose wheel off at around 00:17:27
Main gear off at around 00:25:19
Nose over the end of the asphalt at around 00:27:24
Last usable frame 00:33:20

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

FRAMES_PER_SECOND = 30
# +/- error in time measurements
ERROR_TIMESTAMP_FRAMES = 5.0
ERROR_TIMESTAMP = ERROR_TIMESTAMP_FRAMES / FRAMES_PER_SECOND


class VideoTime(collections.namedtuple('VideoTime', 'min, sec, frame')):

    @property
    def time(self):
        return self.min * 60.0 + self.sec + self.frame / 30.0


VIDEO_BEGIN = VideoTime(0, 0, 0)
VIDEO_END = VideoTime(0, 33, 20)
VIDEO_MAX_AS_INT = int(VIDEO_END.time + 1)


AircraftAspect = collections.namedtuple('AircraftAspect', 'video_time, angle, note')

AIRCRAFT_ASPECTS = (
    AircraftAspect(VideoTime(0, 1, 5), 360 - 18.8, 'Nose to LH front of number 3.'),
    AircraftAspect(VideoTime(0, 4, 1), 360 - 21.5, 'Nose to front centre of number 3.'),
    AircraftAspect(VideoTime(0, 6, 24), 360 - 23.7, 'Nose to RH front of number 3.'),
    AircraftAspect(VideoTime(0, 15, 15), 360 - 29.4, 'Number 1 to tailfin tip.'),
    # Original measurements at same point in time:
    # AircraftAspect(VideoTime(0, 16, 9), 360 - 32.9, 'Nose to front centre number 4.'),
    # AircraftAspect(VideoTime(0, 16, 9), 360 - 32.0, 'Front right number 1 to left tail L/E root.'),
    # Replace by average:
    AircraftAspect(VideoTime(0, 16, 9), 360 - (32.9 + 32.0) / 2,
                   'Average of:Nose to front centre number 4 and Front right number 1 to left tail L/E root.'),
    AircraftAspect(VideoTime(0, 17, 23), 360 - 36.5, 'Right windscreen to right wing tip.'),
    AircraftAspect(VideoTime(0, 21, 18), 360 - 44.5, 'Left wing tip to left tail tip.'),
    AircraftAspect(VideoTime(0, 23, 28), 360 - 55.3, 'Left wing tip to tail fin tip.'),
    AircraftAspect(VideoTime(0, 25, 19), 360 - 65.1, 'Left wing tip to left tail L/E root.'),
    AircraftAspect(VideoTime(0, 29, 21), 360 - 90.0, 'Engines, U/C line up.'),
    AircraftAspect(VideoTime(0, 32, 18), 360 - 105.8, 'Left wing tip to end of row of windows.'),
)

# +/- error in aspect measurements in degrees
ERROR_ASPECT = 2.0

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
        return (self.video_to.time + self.video_from.time) / 2.0

    @property
    def dt(self):
        return self.video_to.time - self.video_from.time


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
    AircraftTransit(VideoTime(0, 7, 24), VideoTime(0, 8, 22), 'Far comms tower number 3.'),
    AircraftTransit(VideoTime(0, 8, 14), VideoTime(0, 9, 11), 'Far comms tower number 4.'),
    AircraftTransit(VideoTime(0, 9, 3), VideoTime(0, 10, 0), 'Far comms tower number 5.'),
    AircraftTransit(VideoTime(0, 9, 11), VideoTime(0, 10, 8), 'Near lamp post number 5.'),
    AircraftTransit(VideoTime(0, 9, 23), VideoTime(0, 10, 20), 'Far comms tower number 6.'),
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
    AircraftTransit(VideoTime(0, 14, 14), VideoTime(0, 15, 1), 'Palm tree (tail cone obscured).'),
    AircraftTransit(VideoTime(0, 15, 5), VideoTime(0, 16, 0), 'Far comms tower number 12.'),
    AircraftTransit(VideoTime(0, 15, 11), VideoTime(0, 16, 6), 'Near lamp post number 9.'),
    AircraftTransit(VideoTime(0, 15, 24), VideoTime(0, 16, 18.5), 'Near lamp post number 10.'),
    AircraftTransit(VideoTime(0, 16, 3), VideoTime(0, 16, 27), 'Far comms tower number 12.'),
    AircraftTransit(VideoTime(0, 16, 16.5), VideoTime(0, 17, 11), 'Far comms tower number 13.'),
    AircraftTransit(VideoTime(0, 16, 27), VideoTime(0, 17, 21), 'Far comms tower number 14.'),
    AircraftTransit(VideoTime(0, 17, 9), VideoTime(0, 18, 3), 'Centre of control tower (also near lamp post number 11.'),
    AircraftTransit(VideoTime(0, 18, 2), VideoTime(0, 18, 26), 'Far comms tower number 15.'),
    AircraftTransit(VideoTime(0, 18, 11), VideoTime(0, 19, 5), 'Far comms tower number 16.'),
    AircraftTransit(VideoTime(0, 19, 9), VideoTime(0, 20, 2), 'Extreme right edge of near signage #1.'),
    AircraftTransit(VideoTime(0, 19, 26.5), VideoTime(0, 20, 19), 'Extreme left edge of near signage #1.'),
    AircraftTransit(VideoTime(0, 20, 20), VideoTime(0, 21, 12.5), 'Centre of chequered control point.'),
    AircraftTransit(VideoTime(0, 21, 15), VideoTime(0, 22, 8), 'Near lamp post number 11.'),
    AircraftTransit(VideoTime(0, 21, 28), VideoTime(0, 22, 20), 'Antenna.'),
    AircraftTransit(VideoTime(0, 22, 6), VideoTime(0, 22, 29), 'Antenna.'),
    AircraftTransit(VideoTime(0, 22, 29), VideoTime(0, 23, 21.5), 'Antenna beyond chequered building.'),
    AircraftTransit(VideoTime(0, 24, 3), VideoTime(0, 24, 25), 'Right edge of far tree.'),
    AircraftTransit(VideoTime(0, 24, 14), VideoTime(0, 25, 4), 'Right edge of far treeline.'),
    AircraftTransit(VideoTime(0, 26, 6.5), VideoTime(0, 26, 28.5), 'Extreme left edge of near signage #2.'),
    AircraftTransit(VideoTime(0, 27, 20), VideoTime(0, 28, 11), 'Distant large radio tower.'),
    AircraftTransit(VideoTime(0, 28, 22), VideoTime(0, 29, 13), 'Large tower.'),
    AircraftTransit(VideoTime(0, 31, 23), VideoTime(0, 32, 13), 'Edge of cables in the foreground.'),
    AircraftTransit(VideoTime(0, 32, 2), VideoTime(0, 32, 22), 'Right edge of poll for cables in the foreground.'),
)

# Nose to tailcone in metres
# Reference: https://en.wikipedia.org/wiki/Airbus_A340 A340-300
TRANSIT_REFERENCE_LENGTH = 63.6

# +/- error in transit delta time measurements in seconds, say +/- 1 frames
ERROR_TRANSIT = 1.0 / 30
