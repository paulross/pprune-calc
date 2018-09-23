import bisect
import collections
import itertools
import math
import sys
import typing

import numpy

from analysis import video_data
from analysis.plot import print_gnuplot


def m_p_s_to_knots(v: float) -> float:
    """Convert m/s to knots."""
    return 3600.0 * v / 0.3048 / 6080


def knots_to_m_p_s(v: float) -> float:
    """Convert knots to m/s."""
    return v * 6080 * 0.3048 / 3600


def num_k_of_n(n: int, k: int) -> int:
    """Return number of combinations of k elements out of n."""
    if k > n:
        return 0
    if k == n:
        return 1
    return math.factorial(n) // (math.factorial(k) * math.factorial((n - k)))


def triangle_ASA(alpha: float, c: float, beta: float) -> typing.Tuple[float, float, float]:
    """Given angle at A, included side A-B, angle at B of a plane triangle
    this returns side A-C, angle at C, side C-B. Angles in radians.
    See: https://en.wikipedia.org/wiki/Solution_of_triangles#A_side_and_two_adjacent_angles_given_(ASA)
    """
    if alpha <= 0.0:
        raise ValueError('Angle alpha must be > 0.0 not {}'.format(alpha))
    if c <= 0.0:
        raise ValueError('Side c must be > 0.0 not {}'.format(c))
    if beta <= 0.0:
        raise ValueError('Angle beta must be > 0.0 not {}'.format(beta))
    gamma = math.pi - alpha - beta
    factor = c / math.sin(gamma)
    a = factor * math.sin(alpha)
    b = factor * math.sin(beta)
    return b, gamma, a


def aspect_intersection(d0: float, b0: float, d1: float, b1: float) -> typing.Tuple[float, float]:
    """Given distance d0 (metres), bearing b0 (degrees), distance d1 (metres),
    bearing b1 (degrees) this returns d, y (metres) of their intersection."""
    b0 = b0 % 360
    b1 = b1 % 360
    if d1 < d0:
        # Swap positions
        d0, d1 = d1, d0
        b0, b1 = b1, b0
    if b0 < 180:
        y_positive = True
        if b1 < b0:
            raise ValueError('Both bearings must be 0-180, not {} <-> {}'.format(b0, b1))
        beta = math.radians(b0)
        alpha = math.radians(180 - b1)
    else:
        y_positive = False
        if b1 > b0:
            raise ValueError('Both bearings must be 180-360, not {} <-> {}'.format(b0, b1))
        beta = math.radians(360 - b0)
        alpha = math.radians(b1 - 180)
    _b, _gamma, a = triangle_ASA(alpha, d1 - d0, beta)
    d = d0 + a * math.cos(beta)
    y = a * math.sin(beta)
    if y_positive:
        return d, y
    return d, -y


def interpolate(xS: typing.List[float], yS: typing.List[float], x: float) -> float:
    """Linear interpolation with extrapolation."""
    if len(xS) != len(yS):
        raise ValueError('Lengths x: {} != y: {}'.format(len(xS), len(yS)))
    i = bisect.bisect_left(xS, x)
    if i == len(xS):
        if len(xS) < 2:
            raise ValueError('Overflow, can not extrapolate')
        # Extrapolate from end
        dy_dx = (yS[-1] - yS[-2]) / (xS[-1] - xS[-2])
        return yS[-1] + dy_dx * (x - xS[-1])
    if xS[i] == x:
        return yS[i]
    if i == 0:
        if len(xS) < 2:
            raise ValueError('Underflow, can not extrapolate')
        # Extrapolate from end
        dy_dx = (yS[1] - yS[0]) / (xS[1] - xS[0])
        return yS[0] + dy_dx * (x - xS[0])
    dx = xS[i] - xS[i-1]
    frac = (x - xS[i -1]) / dx
    dy = yS[i] - yS[i-1]
    y = yS[i-1] + frac * dy
    return y


def apply_min_max_error(func: typing.Callable, t: float, min_max_t: int, err: float) -> float:
    """If min_max_t is zero this returns the function called with t.
    If min_max_t non zero this applies worst time and measurement error"""
    if min_max_t == 0:
        return func(t)
    assert err >= 0
    if min_max_t > 0:
        if func(t + video_data.ERROR_TIMESTAMP) > func(t):
            return func(t + video_data.ERROR_TIMESTAMP) + err
        else:
            return func(t - video_data.ERROR_TIMESTAMP) + err
    assert min_max_t < 0
    if func(t + video_data.ERROR_TIMESTAMP) < func(t):
        return func(t + video_data.ERROR_TIMESTAMP) - err
    else:
        return func(t - video_data.ERROR_TIMESTAMP) - err


def _aspect(t: float) -> float:
    """Returns the angle between the axis of the aircraft and the observer at time t."""
    xS = [v.video_time.time for v in video_data.AIRCRAFT_ASPECTS]
    yS = [v.angle for v in video_data.AIRCRAFT_ASPECTS]
    return interpolate(xS, yS, t)


def aspect(t: float, min_max_t: int) -> float:
    """If min_max_t is zero this returns the angle between the axis of the aircraft and the observer at time t.
    If min_max_t non zero this applies worst time and measuremnt error"""
    return apply_min_max_error(_aspect, t, min_max_t, video_data.ERROR_ASPECT)


def _pitch(t: float) -> float:
    """Returns the apparent pitch angle of the aircraft at time t.
    Due to camera roll this may not be accurate."""
    xS = [v.video_time.time for v in video_data.AIRCRAFT_PITCHES]
    yS = [v.angle for v in video_data.AIRCRAFT_PITCHES]
    return interpolate(xS, yS, t)


def pitch(t: float, min_max_t: int) -> float:
    """Returns the apparent pitch angle of the aircraft at time t.
    Due to camera roll this may not be accurate.
    If min_max_t non zero this applies worst time and measuremnt error"""
    return apply_min_max_error(_pitch, t, min_max_t, video_data.ERROR_PITCH)


def _transit(t: float) -> float:
    """Returns the apparent transit time, dt, of the aircraft fuselage at time t."""
    xS = [v.time for v in video_data.AIRCRAFT_TRANSITS]
    yS = [v.dt for v in video_data.AIRCRAFT_TRANSITS]
    return interpolate(xS, yS, t)


def transit(t: float, min_max_t: int) -> float:
    """Returns the apparent transit time of the aircraft at time t
    If min_max_t non zero this applies worst time and measurement error"""
    return apply_min_max_error(_transit, t, min_max_t, video_data.ERROR_TRANSIT)


def ground_speed(t: float, min_max_t: int) -> float:
    """Returns the ground speed of the aircraft at time t
    If min_max_t non zero this applies worst time and measurement error"""
    p = pitch(t, min_max_t)
    dt = transit(t, -min_max_t)
    result = math.cos(math.radians(p)) * video_data.TRANSIT_REFERENCE_LENGTH / dt
    return result


def ground_speed_raw(t: float, dt: float, min_max_t: int) -> float:
    p = pitch(t, min_max_t)
    if min_max_t < 0:
        dt += video_data.ERROR_TRANSIT
    elif min_max_t > 0:
        dt -= video_data.ERROR_TRANSIT
    result = math.cos(math.radians(p)) * video_data.TRANSIT_REFERENCE_LENGTH / dt
    return result


def print_aspects():
    for aspect in video_data.AIRCRAFT_ASPECTS:
        print('{:8.1f} {:5.1f}'.format(aspect.video_time.time, aspect.angle))

# print_aspects()

def print_func(func: typing.Callable, lim: int) -> None:
    prev = 0.0
    print(
        '{:>2} {:>8} {:>8} {:>8} {:>8} {:>8}'.format(
            't', 'Value', 'd value', 'v min', 'v max', 'diff'
        )
    )
    for t in range(lim):
        print(
            '{:2d} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}'.format(
                t, func(t, 0), func(t, 0) - prev, func(t, -1), func(t, 1), func(t, 1) - func(t, -1)
            )
        )
        prev = func(t, 0)


def integrate_ground_speed(min_max_t: int) -> typing.Tuple[typing.List[int], typing.List[float]]:
    # TODO: Make general integration function or numpy.trapz()
    times: typing.List[int] = list(range(video_data.VIDEO_MAX_AS_INT))
    gsS: typing.List[float] = [ground_speed(t, min_max_t) for t in times]
    result: typing.List[float] = [0.0,]
    for t in range(1, len(gsS)):
        mean_gs = (gsS[t] + gsS[t-1]) / 2
        result.append(mean_gs + result[-1])
    return times, result


def print_raw_transits():
    prev_frames = 0
    for tran in video_data.AIRCRAFT_TRANSITS:
        frames = tran.dt * 30
        print('{} {:8.3f} {:8.3f} {:8.1f} {:8.1f}'.format(
            tran.start, tran.time, tran.dt, frames, frames - prev_frames)
        )
        prev_frames = frames

def print_observer_postions_combinations_per_second_data() -> numpy.ndarray:
    times, dS = integrate_ground_speed(0)
    aS = [aspect(t, 0) for t in range(video_data.VIDEO_MAX_AS_INT)]
    result: typing.List[typing.Tuple[float, float]] = []
    for i, j in itertools.combinations(range(video_data.VIDEO_MAX_AS_INT), 2):
        if abs(i - j) >= 8:
            d, y = aspect_intersection(dS[i], aS[i], dS[j], aS[j])
            result.append((d, y))
    array = numpy.asarray(result)
    print(
        'd[{:3d}]: Max: {:8.1f} Mean: {:8.1f} StdDev: {:8.1f} Min: {:8.1f}'.format(
            array.shape[0],
            array.max(axis=0)[0],
            array.mean(axis=0)[0],
            array.std(axis=0)[0],
            array.min(axis=0)[0],
        )
    )
    print(
        'y[{:3d}]: Max: {:8.1f} Mean: {:8.1f} StdDev: {:8.1f} Min: {:8.1f}'.format(
            array.shape[0],
            array.max(axis=0)[1],
            array.mean(axis=0)[1],
            array.std(axis=0)[1],
            array.min(axis=0)[1],
        )
    )
    return array


def print_observer_postions_combinations() -> numpy.ndarray:
    times, distances = integrate_ground_speed(0)
    dS = []
    aS = []
    for asp in video_data.AIRCRAFT_ASPECTS:
        dS.append(interpolate(times, distances, asp.video_time.time))
        aS.append(asp.angle)
        print('D: {:8.3f} A: {:8.3f}'.format(dS[-1], aS[-1]))
    result: typing.List[typing.Tuple[float, float]] = []
    for i, j in itertools.combinations(range(len(dS)), 2):
        # Only used pairs where delta distance is > 100m
        if abs(dS[i] - dS[j]) > 1000.0:
            d, y = aspect_intersection(dS[i], aS[i], dS[j], aS[j])
            result.append((d, y))
    array = numpy.asarray(result)
    print(
        'd[{:3d}]: Max: {:8.1f} Mean: {:8.1f} StdDev: {:8.1f} Min: {:8.1f}'.format(
            array.shape[0],
            array.max(axis=0)[0],
            array.mean(axis=0)[0],
            array.std(axis=0)[0],
            array.min(axis=0)[0],
        )
    )
    print(
        'y[{:3d}]: Max: {:8.1f} Mean: {:8.1f} StdDev: {:8.1f} Min: {:8.1f}'.format(
            array.shape[0],
            array.max(axis=0)[1],
            array.mean(axis=0)[1],
            array.std(axis=0)[1],
            array.min(axis=0)[1],
        )
    )
    return array

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

    print('Ground speed (m/s)')
    print_func(ground_speed, 34)
    print_gnuplot(ground_speed, slice(0, 34, 1), 'Title', ['Notes',])
    print_raw_transits()

    # ground_speeds = [ground_speed(t, 0) for t in range(video_data.VIDEO_MAX_AS_INT)]
    # dist_false = integrate_ground_speed(0, use_mid_pos=False)
    # dist_true = integrate_ground_speed(0, use_mid_pos=True)
    # assert len(ground_speeds) == len(dist_true)
    # assert len(dist_false) == len(dist_true)
    #
    # for i, (gs, d_f, d_t) in enumerate(zip(ground_speeds, dist_false, dist_true)):
    #     print('{:2d} {:8.3f} {:8.3f} {:8.3f}'.format(i, gs, d_f, d_t))

    # print_observer_postions_combinations()

    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
