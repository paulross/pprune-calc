# import enum
import collections
import itertools
import math
import sys
import typing

import numpy as np
from scipy.optimize import curve_fit

from analysis import aspect
from analysis import pitch
from analysis import video_data
from analysis import video_utils


# class SpeedUnits(enum.Enum):
#     M_PER_SEC = enum.auto()
#     KNOTS = enum.auto()

# def _pitch(t: float) -> float:
#     """Returns the apparent pitch angle of the aircraft at time t.
#     Due to camera roll this may not be accurate."""
#     xS = [v.video_time.time for v in video_data.AIRCRAFT_PITCHES]
#     yS = [v.angle for v in video_data.AIRCRAFT_PITCHES]
#     return video_utils.interpolate(xS, yS, t)
#
#
# def pitch(t: float, min_mid_max: video_data.ErrorDirection) -> float:
#     """Returns the apparent pitch angle of the aircraft at time t.
#     Due to camera roll this may not be accurate.
#     If min_mid_max non zero this applies worst time and measurement error"""
#     return video_utils.apply_min_mid_max_error(_pitch, t, min_mid_max, video_data.ERROR_PITCH)
#
#
def _transit(t: float) -> float:
    """Returns the apparent transit time, dt, of the aircraft fuselage at time t."""
    xS = [v.time for v in video_data.AIRCRAFT_TRANSITS]
    yS = [v.dt for v in video_data.AIRCRAFT_TRANSITS]
    return video_utils.interpolate(xS, yS, t)


def transit(t: float, min_mid_max: video_data.ErrorDirection) -> float:
    """Returns the apparent transit time of the aircraft at time t
    If min_mid_max non zero this applies worst time and measurement error"""
    # TODO: Variable error depending on aspect. i.e. 1 / sin(aspect)
    return video_utils.apply_min_mid_max_error(_transit, t, min_mid_max, video_data.ERROR_TRANSIT)


def ground_speed_raw(t: float,
                     dt: float,
                     min_mid_max: video_data.ErrorDirection) -> float:
    """Calculates ground speed in m/s from the raw t and dt taking length of aircraft
    and pitch interpolated for time t. The error term is increased when the aspect
    strays from 90 degrees."""
    # For aspect flip min_mid_max as we divide to create worst error
    if min_mid_max == video_data.ErrorDirection.MIN:
        asp: float = aspect.aspect_from_fit(t, aspect.ASPECT_FIT[video_data.ErrorDirection.MAX])
        dt += video_data.ERROR_TRANSIT / abs(math.sin(math.radians(asp)))
    elif min_mid_max == video_data.ErrorDirection.MAX:
        asp: float = aspect.aspect_from_fit(t, aspect.ASPECT_FIT[video_data.ErrorDirection.MIN])
        dt -= video_data.ERROR_TRANSIT / abs(math.sin(math.radians(asp)))
    p = pitch.pitch(t, min_mid_max)
    corrn_pitch = math.cos(math.radians(p))
    result = corrn_pitch * video_data.TRANSIT_REFERENCE_LENGTH / dt
    return result


def ground_speeds(min_mid_max: video_data.ErrorDirection) -> np.ndarray:
    """Returns a two columns array of time (s) and ground speed (m/s) for the
    observed transits."""
    data = []
    for transit in video_data.AIRCRAFT_TRANSITS:
        t = transit.time
        dt = transit.dt
        data.append(
            (t, ground_speed_raw(t, dt, min_mid_max))
        )
    return np.array(data, dtype=np.float64)


def ground_speed_timebase() -> np.ndarray:
    """Returns a vector of times of the measured ground speed points."""
    return ground_speeds(video_data.ErrorDirection.MID)[:, 0]


def ground_speed_curve_fit(min_mid_max: video_data.ErrorDirection) -> typing.List[float]:
    gs_array = ground_speeds(min_mid_max)
    # Third order polynomial
    popt, pcov = curve_fit(
        video_utils.polynomial_3,
        gs_array[:, 0],
        gs_array[:, 1],
    )
    return popt


def ground_speed_curve_fit_with_offset(offset: float) -> typing.List[float]:
    gs_array = ground_speeds(video_data.ErrorDirection.MID)
    # Third order polynomial
    popt, pcov = curve_fit(
        video_utils.polynomial_3,
        gs_array[:, 0],
        gs_array[:, 1] + offset,
    )
    return popt


def ground_speed_from_fit(t: float, fit: typing.List[float]) -> float:
    return video_utils.polynomial_3(t, *fit)


def ground_speed_integral(t0: float, t1: float, fit: typing.List[float]) -> float:
    return video_utils.polynomial_3_integral(t0, t1, *fit)


def ground_speed_differential(t: float, fit: typing.List[float]) -> float:
    return video_utils.polynomial_3_differential(t, *fit)


def print_aspects():
    for aspect in video_data.AIRCRAFT_ASPECTS:
        print('{:8.1f} {:5.1f}'.format(aspect.video_time.time, aspect.angle))

# ============ Bearings to the observer =================

def create_time_distance_aspect_array(min_mid_max: video_data.ErrorDirection=video_data.ErrorDirection.MID) -> np.ndarray:
    """Returns a three columns array of (time, distance, aspect) where time
    is the time of grounds speed measurements, distance the integral of the
    ground speed curve fit and aspect the interpolated aspect at that time."""
    gs_fit = ground_speed_curve_fit(min_mid_max)
    aspect_fit = aspect.aspects_curve_fit(video_data.ErrorDirection.MID)
    result = np.column_stack(
        (
            ground_speed_timebase(),
            [
                ground_speed_integral(0, t, gs_fit) for t in ground_speed_timebase()
            ],
            [
                aspect.aspect_from_fit(t, aspect_fit) for t in ground_speed_timebase()
            ],
        )
    )
    return result


def observer_position_combinations(
        min_mid_max: video_data.ErrorDirection=video_data.ErrorDirection.MID,
        baseline: float=0.0,
        ignore_first_n: int=0,
        t_range: typing.Tuple[float, float]=(0.0, 0.0)) -> typing.Tuple[np.ndarray, int]:
    """
    Observer positions are computed for each aspect observation.
    Returns an 2D array of x/y estimates of the observer position and the possible position
    combinations (k out of n).
    Only x positions separated by > baseline are considered. If this is zero then the
    array has all possible positions.

    Error min/max with min_mid_max:
    We always use ground_speed_curve_fit(video_data.ErrorDirection.MID) but apply the error
    to observer_time_distance_bearing or observer_time_distance_bearing_from_wing_tips
    """
    # Use the mid value of distance
    gs_fit = ground_speed_curve_fit(video_data.ErrorDirection.MID)
    # TODO: Only include measurements during a certain time from/to.
    # For example during the ground run and after the ground run - where a yaw into
    # a crosswind might have take place.
    # time_distance_aspect_array = observer_time_distance_bearing(gs_fit)[ignore_first_n:]
    time_distance_aspect_array = observer_time_distance_bearing_from_wing_tips(
        gs_fit,
        min_mid_max,
    )
    time_distance_aspect_array = time_distance_aspect_array[ignore_first_n:]

    if t_range[0] < t_range[1]:
        time_distance_aspect_array = time_distance_aspect_array[
            # Match criteria
            time_distance_aspect_array[:,0] >= t_range[0]
        ]
        time_distance_aspect_array = time_distance_aspect_array[
            # Match criteria
            time_distance_aspect_array[:,0] < t_range[1]
        ]
    temp: typing.List[typing.Tuple[float, float]] = []
    possible_count = 0
    for i, j in itertools.combinations(range(len(time_distance_aspect_array)), 2):
        d0 = time_distance_aspect_array[i, 1]
        d1 = time_distance_aspect_array[j, 1]
        if abs(d0 - d1) > baseline:
            temp.append(
                video_utils.aspect_intersection(
                    time_distance_aspect_array[i, 1],
                    time_distance_aspect_array[i, 2],
                    time_distance_aspect_array[j, 1],
                    time_distance_aspect_array[j, 2]
                )
            )
        possible_count += 1
    result = np.asarray(temp)
    result.sort(axis=0)
    return result, possible_count


def observer_position_mean_std(
        baseline: float=0.0,
        ignore_first_n: int=0,
        t_range: typing.Tuple[float, float]=(0.0, 0.0)) \
        -> typing.Tuple[typing.Tuple[float, float], typing.Tuple[float, float]]:
    """Returns a pair of pairs ((x_mean, x_std), (y_mean, y_std))"""
    combinations, count = observer_position_combinations(
        video_data.ErrorDirection.MID,
        baseline, ignore_first_n, t_range
    )
    x_mean, y_mean = np.mean(combinations, axis=0)
    x_std, y_std= np.std(combinations, axis=0)
    return ((x_mean, x_std), (y_mean, y_std))


def time_distance_bearing_from_fits(time_interval: float=1.0) -> np.ndarray:
    """
    Returns a four column array of (time, distance, bearing, bearing_error) from the fitted
    curves of ground speed and aspect to the observer for all given time intervals.
    Units are (s, m, deg, deg)
    """
    gs_fit = ground_speed_curve_fit(video_data.ErrorDirection.MID)
    aspects_fit = aspect.aspects_curve_fit(video_data.ErrorDirection.MID)
    t = 0.0
    temp = []
    while t <= video_data.TIME_VIDEO_MAX_AS_INT:
        gs = ground_speed_from_fit(t, gs_fit)
        distance = ground_speed_integral(0, t, gs_fit)
        bearing = aspect.aspect_from_fit(t, aspects_fit)
        temp.append((t, distance, bearing, video_data._ERROR_ASPECT))
        t += time_interval
    return np.asarray(temp)


def observer_position_combinations_from_fits(
        baseline: float=0.0,
        time_interval: float=1.0,
        ) -> typing.Tuple[np.ndarray, int]:
    """
    Observer positions are computed for each time_interval for the fitted estimate of
    ground speed and aspect.
    Returns an 2D array of x/y estimates of the observer position and the possible position
    combinations (k out of n).
    Only x positions separated by > baseline are considered. If this is zero then the
    array has all possible positions.
    """
    time_distance_aspect_array = time_distance_bearing_from_fits(time_interval)
    temp: typing.List[typing.Tuple[float, float]] = []
    possible_count = 0
    for i, j in itertools.combinations(range(len(time_distance_aspect_array)), 2):
        d0 = time_distance_aspect_array[i, 1]
        d1 = time_distance_aspect_array[j, 1]
        if abs(d0 - d1) > baseline:
            temp.append(
                video_utils.aspect_intersection(
                    time_distance_aspect_array[i, 1],
                    time_distance_aspect_array[i, 2],
                    time_distance_aspect_array[j, 1],
                    time_distance_aspect_array[j, 2]
                )
            )
        possible_count += 1
    result = np.asarray(temp)
    return result, possible_count


def print_observer_position_combinations(baseline: float) -> np.ndarray:
    # observer_xy, possible = observer_position_combinations(baseline)
    observer_xy, possible = observer_position_combinations_from_fits(baseline=baseline)
    print('print_observer_postions_combinations():')
    print('Points: {:d}'.format(len(observer_xy)))
    print('Combos: {:d}'.format(possible))
    print(
        'x[{:3d}]: Mean: {:8.1f} StdDev: {:8.1f} Min: {:8.1f} Max: {:8.1f} Diff: {:8.1f}'.format(
            observer_xy.shape[0],
            observer_xy.mean(axis=0)[0],
            observer_xy.std(axis=0)[0],
            observer_xy.min(axis=0)[0],
            observer_xy.max(axis=0)[0],
            observer_xy.max(axis=0)[0] - observer_xy.min(axis=0)[0],
        )
    )
    print(
        'y[{:3d}]: Mean: {:8.1f} StdDev: {:8.1f} Min: {:8.1f} Max: {:8.1f} Diff: {:8.1f}'.format(
            observer_xy.shape[0],
            observer_xy.mean(axis=0)[1],
            observer_xy.std(axis=0)[1],
            observer_xy.min(axis=0)[1],
            observer_xy.max(axis=0)[1],
            observer_xy.max(axis=0)[1] - observer_xy.min(axis=0)[1],
        )
    )
    for i in range(len(observer_xy)):
        print('{:.1f} {:.1f}'.format(observer_xy[i, 0], observer_xy[i, 1]))


def _observer_time_distance_bearing(
        gs_fit: typing.List[float],
        aspect_data: typing.Sequence[typing.Union[video_data.AircraftAspect, video_data.AircraftAspectWingTips]],
        min_mid_max: video_data.ErrorDirection) -> np.ndarray:
    """
    Returns a three column array of (time, distance, aspect, aspect_error) from the observed aspect data.
    Units are (seconds, metres, degrees, degrees).
    """
    # times = ground_speed_timebase()
    # distances = []
    # for t in times:
    #     distances.append(ground_speed_integral(0, t, gs_fit))
    temp = []
    # aspects_fit = aspect.aspects_curve_fit(video_data.ErrorDirection.MID)
    aspects_fit = aspect.aspects_curve_fit_from_wing_tips(min_mid_max)
    for asp in aspect_data:
        t = asp.video_time.time
        distance = ground_speed_integral(0, t, gs_fit)
        # bearing = asp.angle
        # Use the aspects fit for smoothness
        bearing = video_utils.polynomial_3(t, *aspects_fit)
        # Allow for assumed yaw of the aircraft from video_date.YAW_PROFILE
        # yaw = video_utils.interpolate(video_data.YAW_PROFILE[:, 0], video_data.YAW_PROFILE[:, 1], t)
        # print('TRACE: t={:6.1f} yaw={:6.1f}'.format(t, yaw))
        # bearing += yaw
        temp.append((t, distance, bearing, asp.error))
    array = np.asarray(temp)
    return array

def observer_time_distance_bearing(
        gs_fit: typing.List[float],
        min_mid_max: video_data.ErrorDirection,
        ) -> np.ndarray:
    """
    Returns a three column array of (time, distance, aspect, aspect_error) from the observed aspect data of
    transits of parts of the aircraft. Distance is the integral of the ground speed (so from start of video).
    Units are (seconds, metres, degrees, degrees).
    """
    temp = []
    # aspects_fit = aspect.aspects_curve_fit(video_data.ErrorDirection.MID)
    # aspects_fit = aspect.aspects_curve_fit_from_wing_tips(min_mid_max)
    for asp in video_data.AIRCRAFT_ASPECTS:
        t = asp.video_time.time
        distance = ground_speed_integral(0, t, gs_fit)
        # bearing = asp.angle
        # Use the aspects fit for smoothness
        # bearing = video_utils.polynomial_3(t, *aspects_fit)
        # Allow for assumed yaw of the aircraft from video_date.YAW_PROFILE
        # yaw = video_utils.interpolate(video_data.YAW_PROFILE[:, 0], video_data.YAW_PROFILE[:, 1], t)
        # print('TRACE: t={:6.1f} yaw={:6.1f}'.format(t, yaw))
        # bearing += yaw
        temp.append((t, distance, asp.angle, asp.error))
    array = np.asarray(temp)
    return array

def observer_time_distance_bearing_from_wing_tips(
        gs_fit: typing.List[float],
        min_mid_max: video_data.ErrorDirection,
        ) -> np.ndarray:
    temp = []
    # aspects_fit = aspect.aspects_curve_fit(video_data.ErrorDirection.MID)
    # aspects_fit = aspect.aspects_curve_fit_from_wing_tips(min_mid_max)
    for asp in video_data.AIRCRAFT_ASPECTS_FROM_WING_TIPS:
        t = asp.video_time.time
        distance = ground_speed_integral(0, t, gs_fit)
        # bearing = asp.angle
        # Use the aspects fit for smoothness
        # bearing = video_utils.polynomial_3(t, *aspects_fit)
        # Allow for assumed yaw of the aircraft from video_date.YAW_PROFILE
        # yaw = video_utils.interpolate(video_data.YAW_PROFILE[:, 0], video_data.YAW_PROFILE[:, 1], t)
        # print('TRACE: t={:6.1f} yaw={:6.1f}'.format(t, yaw))
        # bearing += yaw
        if min_mid_max == video_data.ErrorDirection.MIN:
            temp.append((t, distance, asp.angle - asp.error, asp.error))
        elif min_mid_max == video_data.ErrorDirection.MID:
            temp.append((t, distance, asp.angle, asp.error))
        elif min_mid_max == video_data.ErrorDirection.MAX:
            temp.append((t, distance, asp.angle + asp.error, asp.error))
        else:
            assert 0
    array = np.asarray(temp)
    return array


"""Returns a three columns array of (time, distance, aspect) where time
    is the time of grounds speed measurements, distance the integral of the
    ground speed curve fit and aspect the interpolated aspect at that time."""


TimeXaxisDistanceLabel = collections.namedtuple('TimeXaxisDistanceLabel', 'time, distance, label')


def transit_x_axis_distances(observer_x: float, observer_y: float) -> typing.List[TimeXaxisDistanceLabel]:
    """
    Returns a list of TimeXaxisDistanceLabel of the observed transits for a give observer position
    where the .distance is the x axis value in metres from the start of the runway.
    """
    result = []
    for t, label in video_data.GOOGLE_EARTH_EVENTS:
        # lat, lon = video_data.GOOGLE_EARTH_POSITIONS_LAT_LONG[k]
        # event_time = video_data.GOOGLE_EARTH_EVENT_MAP[k]
        # x, y = video_utils.lat_long_to_xy(
        #     video_data.GOOGLE_EARTH_DATUM_LAT_LONG[0],
        #     video_data.GOOGLE_EARTH_DATUM_LAT_LONG[1],
        #     video_data.GOOGLE_EARTH_X_AXIS,
        #     lat,
        #     lon,
        # )
        x, y = video_data.GOOGLE_EARTH_POSITIONS_XY[label]
        x_intercept = video_utils.transit_x_axis_intercept(x, y, observer_x, observer_y)
        result.append(TimeXaxisDistanceLabel(t, x_intercept, label))
    return result


def camera_angle_of_view(min_mid_max: video_data.ErrorDirection = video_data.ErrorDirection.MID) -> np.ndarray:
    # TODO: Figure out min/max error terms.
    # Max value is obtained with:
    # max alpha, min d, min pitch
    # Min value is obtained with:
    # min alpha, max d, max pitch
    gs_fit = ground_speed_curve_fit(-min_mid_max)
    # aspect_fit = aspect.aspects_curve_fit(min_mid_max)
    pitch_data = pitch.pitches(-min_mid_max)

    OBSERVER_POSITION_X = 2250
    OBSERVER_POSITION_Y = -750

    for data in video_data.AIRCRAFT_LENGTH_IN_PIXELS:
        t = data.video_time.time
        px = data.length_px
        x = OBSERVER_POSITION_X - ground_speed_integral(0, t, gs_fit)
        d = math.sqrt(x**2 + OBSERVER_POSITION_Y**2)
        alpha = abs(math.atan2(OBSERVER_POSITION_Y, x))
        pitch_angle = video_utils.interpolate(pitch_data[:, 0], pitch_data[:, 1], t)
        apparent_length = video_data.TRANSIT_REFERENCE_LENGTH * math.sin(alpha) * math.cos(math.radians(pitch_angle))
        px_per_m = px / apparent_length
        width_in_m = video_data.SCREENSHOT_WIDTH / px_per_m
        angle_of_view = math.degrees(2 * math.atan(width_in_m / (2 * d)))
        print('{:<4.1f} {:6.3f}'.format(t, angle_of_view))

def camera_angle_of_view_with_errors() -> np.ndarray:
    pass

# ============ END: Bearings to the observer =================


def main():
    # print('Aspect')
    # # for t in range(34):
    # #     print('{:2d} {:8.3f} {:8.3f} {:8.3f} {:8.3f}'.format(t, aspect(t, 0), aspect(t, -1), aspect(t, 1), aspect(t, -1) - aspect(t, 1)))
    # print_func(aspect, 34)
    # print()

    # print('Pitch')
    # # for t in range(34):
    # #     print('{:2d} {:8.3f} {:8.3f} {:8.3f} {:8.3f}'.format(t, pitch(t, 0), pitch(t, -1), pitch(t, 1), pitch(t, -1) - pitch(t, 1)))
    # print_func(pitch, 34)
    # print()

    # print('Transits')
    # print_func(transit, 34)
    # print()

    # print_raw_transits()

    # ground_speeds = [ground_speed(t, 0) for t in range(video_data.VIDEO_MAX_AS_INT)]
    # dist_false = integrate_ground_speed(0, use_mid_pos=False)
    # dist_true = integrate_ground_speed(0, use_mid_pos=True)
    # assert len(ground_speeds) == len(dist_true)
    # assert len(dist_false) == len(dist_true)
    #
    # for i, (gs, d_f, d_t) in enumerate(zip(ground_speeds, dist_false, dist_true)):
    #     print('{:2d} {:8.3f} {:8.3f} {:8.3f}'.format(i, gs, d_f, d_t))

    # print_observer_position_combinations(1250)
    # print(observer_time_distance_bearing())

    # print(ground_speed_curve_fit(video_data.ErrorDirection.MID))

    camera_angle_of_view()

    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
