import collections
import datetime
import math
import pprint
import sys
import typing

DataPoint = collections.namedtuple('DataPoint', 'id, aperture, focal_length, time, lat, long, altitude')

DATA: typing.Tuple[DataPoint] = (
    DataPoint(405, 20, 17, datetime.datetime(2017, 12, 31, 15, 11, 50), -33.599550, 151.215141, 43, ),
    DataPoint(406, 18, 17, datetime.datetime(2017, 12, 31, 15, 11, 57), -33.598109, 151.216812, 77, ),
    DataPoint(407, 16, 17, datetime.datetime(2017, 12, 31, 15, 12,  7), -33.595871, 151.218732, 140, ),
    DataPoint(408, 14, 41, datetime.datetime(2017, 12, 31, 15, 12, 13), -33.594448, 151.219963, 140, ),
    DataPoint(410, 14, 41, datetime.datetime(2017, 12, 31, 15, 12, 23), -33.593285, 151.222965, 175, ),
    DataPoint(412, 14, 41, datetime.datetime(2017, 12, 31, 15, 12, 29), -33.593329, 151.225653, 175, ),
)

# 1nm is 1852m exactly: https://en.wikipedia.org/wiki/Knot_(unit)
KT_PER_M_S = 3.6 / 1.852
M_PER_DEGREE = 1852 * 60
# Degrees per second: https://en.wikipedia.org/wiki/Standard_rate_turn
STANDARD_RATE_TURN = 3.0

SpeedDirection = collections.namedtuple('SpeedDirection', 'speed, direction')


def airspeed_heading(ground: SpeedDirection, wind: SpeedDirection) -> SpeedDirection:
    """Given ground speed/track and wind speed/direction this returns the airspeed/heading."""
    wind_head = wind.speed * math.cos(math.radians(wind.direction - ground.direction))
    wind_cros = wind.speed * math.sin(math.radians(wind.direction - ground.direction))
    drift = math.degrees(math.atan2(wind_cros, ground.speed + wind_head))
    hdg = ground.direction + drift
    v_air = math.sqrt((ground.speed + wind_head)**2 + wind_cros)
    return SpeedDirection(v_air, hdg)


WIND = SpeedDirection(15, 25)


def compute():
    prev_hdg = None
    ret = [
        (
            'Photos',
            '∆N (m)', '∆E (m)', 'd (m)',
            '∆t (s)',
            'g/s (kt)', '± (kt)', 'trk (°)',
            'a/s (kt)', '± (kt)', 'hdg (°)',
            'roc, fpm', '± (fpm)', 'rot (°/s)',
        )
    ]
    for i in range(1, len(DATA)):
        a: DataPoint = DATA[i-1]
        b: DataPoint = DATA[i]
        dlat = b.lat - a.lat
        dlon = b.long - a.long
        lat_mid = (b.lat + a.lat) / 2.0
        dlat_m = M_PER_DEGREE * dlat
        dlon_m = M_PER_DEGREE * dlon * math.cos(math.radians(lat_mid))
        d = math.sqrt(dlat_m**2 + dlon_m**2)
        track = math.degrees(math.atan2(dlon_m, dlat_m))
        dt_s = (b.time - a.time).total_seconds()
        ground = SpeedDirection(KT_PER_M_S * d / dt_s, track)
        as_hdg = airspeed_heading(ground, WIND)
        roc_ft_s = 60 * (b.altitude - a.altitude) / dt_s
        if prev_hdg is None:
            rot = 'N/A'
        else:
            rot = '{:.1f}'.format((as_hdg.direction - prev_hdg) / dt_s)# / STANDARD_RATE_TURN)
        ret.append(
            [
                '{a_id:d}->{b_id:d}'.format(a_id=a.id, b_id=b.id),
                dlat_m, dlon_m, d,
                dt_s,
                ground.speed, ground.speed / dt_s, ground.direction,
                as_hdg.speed, as_hdg.speed / dt_s, as_hdg.direction,
                roc_ft_s, roc_ft_s / dt_s, rot
            ]
        )
        prev_hdg = as_hdg.direction
    return ret


# Typical output:
# /Users/paulross/venvs/pprune_A340/bin/python /Users/paulross/Documents/workspace/pprune-calc/VH_NOO/vh_noo.py
# (DataPoint(id=405, aperture=20, focal_length=17, time=datetime.datetime(2017, 12, 31, 15, 11, 50), lat=-33.59955, long=151.215141, altitude=43),
#  DataPoint(id=406, aperture=18, focal_length=17, time=datetime.datetime(2017, 12, 31, 15, 11, 57), lat=-33.598109, long=151.216812, altitude=77),
#  DataPoint(id=407, aperture=16, focal_length=17, time=datetime.datetime(2017, 12, 31, 15, 12, 7), lat=-33.595871, long=151.218732, altitude=140),
#  DataPoint(id=408, aperture=14, focal_length=41, time=datetime.datetime(2017, 12, 31, 15, 12, 13), lat=-33.594448, long=151.219963, altitude=140),
#  DataPoint(id=410, aperture=14, focal_length=41, time=datetime.datetime(2017, 12, 31, 15, 12, 23), lat=-33.593285, long=151.222965, altitude=175),
#  DataPoint(id=412, aperture=14, focal_length=41, time=datetime.datetime(2017, 12, 31, 15, 12, 29), lat=-33.593329, long=151.225653, altitude=175))
# Wind: SpeedDirection(speed=15, direction=25)
#
#   Photos |   ∆N (m) |   ∆E (m) |    d (m) |   ∆t (s) | g/s (kt) |   ± (kt) |  trk (°) | a/s (kt) |   ± (kt) |  hdg (°) | roc, fpm |  ± (fpm) | rot (°/s)
# 405->406 |    160.1 |    154.7 |    222.6 |      7.0 |     61.8 |      8.8 |     44.0 |     76.0 |     10.9 |     40.3 |    291.4 |     41.6 |      N/A
# 406->407 |    248.7 |    177.7 |    305.7 |     10.0 |     59.4 |      5.9 |     35.5 |     74.1 |      7.4 |     33.4 |    378.0 |     37.8 |     -0.7
# 407->408 |    158.1 |    113.9 |    194.9 |      6.0 |     63.1 |     10.5 |     35.8 |     77.9 |     13.0 |     33.7 |      0.0 |      0.0 |      0.0
# 408->410 |    129.2 |    277.9 |    306.4 |     10.0 |     59.6 |      6.0 |     65.1 |     71.0 |      7.1 |     57.3 |    210.0 |     21.0 |      2.4
# 410->412 |     -4.9 |    248.8 |    248.9 |      6.0 |     80.6 |     13.4 |     91.1 |     86.6 |     14.4 |     82.1 |      0.0 |      0.0 |      4.1
#
# Process finished with exit code 0


def main():
    pprint.pprint(DATA)
    print('Wind:', WIND)
    print()
    result = compute()
    # pprint.pprint(result)
    print(' | '.join('{:>8}'.format(v) for v in result[0]))
    for row in result[1:]:
        line = [
            '{:>8}'.format(row[0]),
        ]
        line.extend('{:>8.1f}'.format(v) for v in row[1:-1])
        line.append('{:>8}'.format(row[-1]))
        print(' | '.join(line))
    return 0

if __name__ == '__main__':
    sys.exit(main())