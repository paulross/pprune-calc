"""
Thread: https://www.pprune.org/rumours-news/613321-air-x-340-brasil.html

Videos:
https://youtu.be/Y6PNFzVvlWo
https://youtu.be/XbWaXdA5jY0

Other notes (times are mm:ss::ff @ 30 f.p.s)

Nose wheel off at around 00:17:27
Main gear off at around 00:25:19
Nose over the end of the asphalt at around 00:38:11

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

# +/- error in time measurements
ERROR_TIMESTAMP = 0.5

class VideoTime(collections.namedtuple('VideoTime', 'min, sec, frame')):

    @property
    def time(self):
        return self.min * 60.0 + self.sec + self.frame / 30.0


VIDEO_BEGIN = VideoTime(0, 0, 0)
VIDEO_END = VideoTime(0, 33, 16)
VIDEO_MAX_AS_INT = int(VIDEO_END.time + 1)


AircraftAspect = collections.namedtuple('AircraftAspect', 'video_time, angle, note')

AIRCRAFT_ASPECTS = (
    AircraftAspect(VideoTime(0, 1, 5), 360 - 18.8, 'Nose to LH front of number 3.'),
    AircraftAspect(VideoTime(0, 4, 1), 360 - 21.5, 'Nose to front centre of number 3.'),
    AircraftAspect(VideoTime(0, 6, 24), 360 - 23.7, 'Nose to RH front of number 3.'),
    AircraftAspect(VideoTime(0, 15, 15), 360 - 29.4, 'Number 1 to tailfin tip.'),
    # Original measurments at same point in time:
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


    AircraftTransit(VideoTime(0, 28, 22), VideoTime(0, 29, 13), 'Large tower.'),
    AircraftTransit(VideoTime(0, 31, 23), VideoTime(0, 32, 13), 'Edge of cables in the foreground.'),
    AircraftTransit(VideoTime(0, 32, 2), VideoTime(0, 32, 22), 'Poll for cables in the foreground.'),
)

# Nose to tailcone in metres
# Reference: https://en.wikipedia.org/wiki/Airbus_A340 A340-300
TRANSIT_REFERENCE_LENGTH = 63.6

# +/- error in transit delta time measurements in seconds, say +/- 1 frames
ERROR_TRANSIT = 1.0 / 30
