import math
import sys
import typing

import numpy as np
from scipy.optimize import curve_fit

import data.tiles
import map_funcs
from cmn import polynomial

URL = 'https://youtu.be/LtJcgdU5MUk'
FRAME_RATE = 30


def frame_to_time(frame: int) -> float:
    """Return the time in seconds from the start of this video."""
    return map_funcs.frame_to_time(frame, FRAME_RATE)


# Touchdown at about 00:35 [1015], 4 seconds after last position, say 4 * 85 = 340, add 330, so 670m from threshold
# Off runway at about 00:46 [1380], 11 seconds after that, 11 * 70 = 770, add 670, so 1440m from threshold, 200m to go.
# Crosses a pale track at 00:54, [1621], near boundary edge?
# Frame 1685 landing gear hits an obstruction and collapses, boundary fence?
# Breach fence and undercarridge collapse, tile 7, Point(970, 697)
# Frame 1712, camera movement indicates impact.
# Impact site is tile 7, Point(926, 737)
# Impact at 00:57.

# In metres
# DISTANCE_FROM_RUNWAY_END_TO_FENCE = 213.0
# DISTANCE_FROM_FENCE_TO_FINAL_IMPACT = 38.4
# DISTANCE_FROM_RUNWAY_END_TO_FINAL_IMPACT = DISTANCE_FROM_RUNWAY_END_TO_FENCE + DISTANCE_FROM_FENCE_TO_FINAL_IMPACT

FRAME_THRESHOLD = 827
FRAME_TOUCHDOWN = 1015  # Movement of camera due to impact.
FRAME_LAST = 1819

POSITIONS_FROM_TILES: typing.Dict[int, typing.Tuple[int, map_funcs.Point, str]] = {
    1: (1, map_funcs.Point(1207, 749), 'Edge of settlement in line with dark patch on island in the foreground.'),
    87: (1, map_funcs.Point(939, 1087), 'Settlement line with isolated lake and finger into lake.'),
    295: (2, map_funcs.Point(1164, 801), 'Trees and edge of V shaped lake.'),

    483: (3, map_funcs.Point(1258, 627), 'Blue roofed building in line with RHS of larger white building.'),
    555: (3, map_funcs.Point(1040, 903), 'Factory with covered conveyer belt.'),
    593: (3, map_funcs.Point(938, 1033), 'Tree line with red building behind.'),
    621: (3, map_funcs.Point(840, 1159), 'Blue building left lined up with low white building left.'),
    652: (3, map_funcs.Point(736, 1293), 'Crossing road with red building beyond.'),

    704: (4, map_funcs.Point(1246, 581), 'Crossing road with roundabout beyond.'),
    749: (4, map_funcs.Point(1105, 762), 'Crossing boundary fence.'),

    827: (5, map_funcs.Point(1597, 197), 'Crossing the threshold.'),
    # About 280px from threshold
    880: (5, map_funcs.Point(1444, 395), 'Start of the first set of white marker pairs.'),
    888: (5, map_funcs.Point(1418, 423), 'End of the first set of white marker pairs.'),
    932: (5, map_funcs.Point(1290, 585), 'Start of the second set of white marker pairs.'),
    940: (5, map_funcs.Point(1266, 615), 'End of the second set of white marker pairs.'),
}

#======== Slab meaasurements ========

# The estimated error when counting slabs, 10% of slab length
SLAB_LENGTH = 6.0  # Width is 1.8
SLAB_MEASUREMENT_ERROR = SLAB_LENGTH * 0.1
SLAB_TRANSITS: typing.Dict[int, typing.Tuple[int, float]] = {
    841: (2, 1.0),
    864: (8, 3.9),
    # Frame 880 shows a slab edge exactly at the start of the white bars
    # Frame 888 shows a slab edge exactly at the enf of the white bars
    # Bars are 36 pixels long, 9px/slab 9*0.6172839506172839 = 5.55
    880: (8, 4.0),
    895: (8, 4.0),
    918: (12, 5.9),
    # Frames 932-940 is 4 slabs across the bars, as above.
    964: (979-964, 7.0),
    # Touchdown is 1015
    1016: (1031 - 1016, 7.0),
    1053: (1064 - 1053, 5.0),
    1075: (1086 - 1075, 5.0),

    1106: (1115 - 1106, 4.0),
    1119: (1128 - 1119, 4.0),
    1151: (1160 - 1151, 4.0),
    1198: (1205 - 1198, 3.0),
    1222: (1227 - 1222, 2.0),
    1247: (1252 - 1247, 2.0),
    1262: (1267 - 1262, 2.0),
    1293: (1301 - 1293, 3.0),
    1323: (1329 - 1323, 2.2),
    1346: (1352 - 1346, 2.1),
    1370: (1373 - 1370, 1.0),
    # 1384 runway dissapears
}
LAST_MEASURED_FRAME = max(SLAB_TRANSITS.keys()) + SLAB_TRANSITS[max(SLAB_TRANSITS.keys())][0]
LAST_MEASURED_TIME = map_funcs.frame_to_time(LAST_MEASURED_FRAME, FRAME_RATE)


def init_slab_speeds():
    slab_speeds = np.empty((len(SLAB_TRANSITS), 5))
    for f, frame_number in enumerate(sorted(SLAB_TRANSITS.keys())):
        d_frame, d_slab = SLAB_TRANSITS[frame_number]
        dx = d_slab * SLAB_LENGTH
        t = map_funcs.frame_to_time(frame_number + d_frame / 2, FRAME_RATE)
        dt = map_funcs.frames_to_dtime(frame_number, frame_number + d_frame, FRAME_RATE)
        slab_speeds[f][0] = frame_number
        slab_speeds[f][1] = t
        slab_speeds[f][2] = dx / dt
        slab_speeds[f][3] = (dx + SLAB_MEASUREMENT_ERROR) / dt
        slab_speeds[f][4] = (dx - SLAB_MEASUREMENT_ERROR) / dt
    return slab_speeds


SLAB_SPEEDS = init_slab_speeds()

FRAME_EVENTS: typing.Dict[int, str] = {
    1: 'Video start',
    510: 'Maximum ground speed',
    827: 'Threshold',
    1015: 'Touchdown',
    1065: 'First appearance in video B, x=688±19 m',
    1081: 'Start of drift to the right.',
    LAST_MEASURED_FRAME: 'Last speed measurement',
    # At about 46s the starboard undercarriage leg meets the grass.
    # So frame 1 + 30 * 46 = 1381
    1384: 'Runway disappears, data is extrapolated',
    1685: 'Impact with fence',
    1712: 'Final impact?',
    1819: 'Last frame',
}

FRAME_EVENTS_STR_KEY = {v: k for k, v in FRAME_EVENTS.items()}

# This is the best accuracy that we can claim based on the comparison of differentiated tile data
# and the slab data
VIDEO_A_MAX_SPEED_ACCURACY = 2.0


def create_distance_array_of_tile_data() -> typing.Dict[str, np.ndarray]:
    """Returns a numpy array of time, position from the tile position data."""
    columns = ('Frame', 'Time', 'd', 'd+', 'd-')
    ret = {k: np.empty((len(POSITIONS_FROM_TILES), 1)) for k in columns}
    for f, frame_number in enumerate(sorted(POSITIONS_FROM_TILES.keys())):
        t = map_funcs.frame_to_time(frame_number, FRAME_RATE)
        dx = POSITIONS_FROM_TILES[frame_number][1].x \
             - data.tiles.THRESHOLD_ON_EACH_TILE[POSITIONS_FROM_TILES[frame_number][0]].x
        dy = POSITIONS_FROM_TILES[frame_number][1].y \
             - data.tiles.THRESHOLD_ON_EACH_TILE[POSITIONS_FROM_TILES[frame_number][0]].y
        d_threshold = data.tiles.TILE_SCALE_M_PER_PIXEL * math.sqrt(dx ** 2 + dy ** 2)
        if frame_number < FRAME_THRESHOLD:
            d_threshold = -d_threshold
        ret['Frame'][f] = frame_number
        ret['Time'][f] = t
        ret['d'][f] = d_threshold
        ret['d+'][f] = d_threshold + map_funcs.distance_tolerance(d_threshold)
        ret['d-'][f] = d_threshold - map_funcs.distance_tolerance(d_threshold)
    return ret


TILE_D_ORDER = ('d', 'd+', 'd-')


def get_tile_d_fits() -> typing.Tuple[typing.Dict[str, np.ndarray], typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]]]:
    array_dict = create_distance_array_of_tile_data()
    fits = {
        d: curve_fit(polynomial.polynomial_3, array_dict['Time'][:, 0], array_dict[d][:, 0])
        for d in TILE_D_ORDER
    }
    return array_dict, fits


def write_tile_results(stream: typing.TextIO=sys.stdout):
    array_dict = create_distance_array_of_tile_data()
    # Fit curve
    # print(array_dict['d'][:, 0])
    # print(array_dict['Time'][:, 0])
    # popt, pcov = curve_fit(map_funcs.polynomial_3, array_dict['Time'][:, 0], array_dict['d'][:, 0])
    # print('POPT', popt)
    D_FORMULAE = {
        'd': 'distance_mid',
        'd+': 'distance_plus',
        'd-': 'distance_minus',
    }
    array_dict, d_fits = get_tile_d_fits()
    # print('fits', fits)
    # Differentiate for velocity.
    stream.write('# Tile distance data\n')
    for d in TILE_D_ORDER:
        # coeff_str = [f'{v:.3e}' for v in fits[d][0]]
        # stream.write(f'# {d} coefficients: {", ".join(coeff_str)}\n')
        formulae = polynomial.polynomial_string(D_FORMULAE[d], 't', '.3e', *d_fits[d][0])
        stream.write(f'# {formulae}\n')
    # stream.write(f'# d+ coefficients {fits["d+"][0]}\n')
    # stream.write(f'# d- coefficients {fits["d-"][0]}\n')
    stream.write(f'# Columns: frame, t, d, d+, d-, v, v+, v- (m/s), v, v+, v- (knots)\n')
    for i in range(len(array_dict['Frame'])):
        t = array_dict['Time'][i, 0]
        v_m_per_second = [polynomial.polynomial_3_differential(t, *d_fits[k][0]) for k in TILE_D_ORDER]
        v_knots = [map_funcs.metres_per_second_to_knots(v) for v in v_m_per_second]
        row = [
            f'{array_dict["Frame"][i, 0]:<6.0f}',
            f'{t:6.1f}',
            f'{array_dict["d"][i, 0]:8.1f}',
            f'{array_dict["d+"][i, 0]:8.1f}',
            f'{array_dict["d-"][i, 0]:8.1f}',
            f'{v_m_per_second[0]:8.1f}',
            f'{v_m_per_second[1]:8.1f}',
            f'{v_m_per_second[2]:8.1f}',
            f'{v_knots[0]:8.1f}',
            f'{v_knots[1]:8.1f}',
            f'{v_knots[2]:8.1f}',
        ]
        stream.write(' '.join((row)))
        stream.write('\n')


SLAB_V_ORDER = ('v', 'v+', 'v-')


def get_slab_v_fits() -> typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]]:
    v_fits = {
        v_name: curve_fit(polynomial.polynomial_3, SLAB_SPEEDS[:, 1], SLAB_SPEEDS[:, v + 2])
        for v, v_name in enumerate(SLAB_V_ORDER)
    }
    return v_fits


def write_slab_results(stream: typing.TextIO=sys.stdout):
    """Writes out the results from the slab data."""
    columns = ('Frame', 'Time', 'v', 'v+', 'v-', 'd', 'd+', 'd-', 'a', 'a+', 'a-')
    # Compute fits
    # V_ORDER = ('v', 'v+', 'v-')
    V_FORMULAE = {
        'v': 'speed_mid',
        'v+': 'speed_plus',
        'v-': 'speed_minus',
    }
    v_fits = get_slab_v_fits()
    # print(map_data.SLAB_SPEEDS)
    # print('v_fits', v_fits)

    stream.write('# Slab speed data\n')
    for v in SLAB_V_ORDER:
        # coeff_str = [f'{value:.3e}' for value in v_fits[v][0]]
        # stream.write(f'# {v} coefficients: {", ".join(coeff_str)}\n')
        formulae = polynomial.polynomial_string(V_FORMULAE[v], 't', '.3e', *v_fits[v][0])
        stream.write(f'# {formulae}\n')

    THRESHOLD_TIME = map_funcs.frame_to_time(FRAME_THRESHOLD, FRAME_RATE)
    d_offsets = [
        polynomial.polynomial_3_integral(THRESHOLD_TIME, *v_fits["v"][0]),
        polynomial.polynomial_3_integral(THRESHOLD_TIME, *v_fits["v+"][0]),
        polynomial.polynomial_3_integral(THRESHOLD_TIME, *v_fits["v-"][0]),
    ]
    stream.write(f'# d_offsets {d_offsets}\n')
    stream.write(f'# Columns: frame, t, v, v+, v- (m/s), d, d+, d-, a, a+, a-, v, v+, v- (knots)\n')
    for i in range(len(SLAB_SPEEDS)):
        t = SLAB_SPEEDS[i, 1]
        v_m_per_second = [SLAB_SPEEDS[i, j] for j in (2, 3, 4)]
        v_knots = [map_funcs.metres_per_second_to_knots(v) for v in v_m_per_second]
        row = [
            f'{SLAB_SPEEDS[i, 0]:<6.0f}',
            f'{t:6.1f}',
            f'{v_m_per_second[0]:8.1f}',
            f'{v_m_per_second[1]:8.1f}',
            f'{v_m_per_second[2]:8.1f}',
            f'{polynomial.polynomial_3_integral(t, *v_fits["v"][0]) - d_offsets[0]:8.1f}',
            f'{polynomial.polynomial_3_integral(t, *v_fits["v+"][0]) - d_offsets[1]:8.1f}',
            f'{polynomial.polynomial_3_integral(t, *v_fits["v-"][0]) - d_offsets[2]:8.1f}',
            f'{polynomial.polynomial_3_differential(t, *v_fits["v"][0]):8.1f}',
            f'{polynomial.polynomial_3_differential(t, *v_fits["v+"][0]):8.1f}',
            f'{polynomial.polynomial_3_differential(t, *v_fits["v-"][0]):8.1f}',
            f'{v_knots[0]:8.1f}',
            f'{v_knots[1]:8.1f}',
            f'{v_knots[2]:8.1f}',
        ]
        stream.write(' '.join((row)))
        stream.write('\n')


def _compute_distance(
        frame: int,
        tile_d_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]],
        slab_v_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]]) -> typing.Tuple[float, float, float]:
    t = map_funcs.frame_to_time(frame, FRAME_RATE)
    if frame <= FRAME_THRESHOLD:
        # Only use the tile_d_fits
        return (polynomial.polynomial_3(t, *tile_d_fits['d'][0]),
                polynomial.polynomial_3(t, *tile_d_fits['d+'][0]),
                polynomial.polynomial_3(t, *tile_d_fits['d-'][0]))
    else:
        THRESHOLD_TIME = map_funcs.frame_to_time(FRAME_THRESHOLD, FRAME_RATE)
        d_offsets = [
            polynomial.polynomial_3_integral(THRESHOLD_TIME, *slab_v_fits["v"][0]),
            polynomial.polynomial_3_integral(THRESHOLD_TIME, *slab_v_fits["v+"][0]),
            polynomial.polynomial_3_integral(THRESHOLD_TIME, *slab_v_fits["v-"][0]),
        ]
        slab_d = (
            polynomial.polynomial_3_integral(t, *slab_v_fits["v"][0]) - d_offsets[0],
            polynomial.polynomial_3_integral(t, *slab_v_fits["v+"][0]) - d_offsets[1],
            polynomial.polynomial_3_integral(t, *slab_v_fits["v-"][0]) - d_offsets[2],
        )
        if frame > max(POSITIONS_FROM_TILES.keys()):
            # Only use the slab_v_fits
            return slab_d
        else:
            # Use both
            return (
                (polynomial.polynomial_3(t, *tile_d_fits['d'][0]) + slab_d[0]) / 2.0,
                (polynomial.polynomial_3(t, *tile_d_fits['d+'][0]) + slab_d[1]) / 2.0,
                (polynomial.polynomial_3(t, *tile_d_fits['d-'][0]) + slab_d[2]) / 2.0,
            )


def _compute_speed(
        frame: int,
        tile_d_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]],
        slab_v_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]]) -> typing.Tuple[float, float, float]:
    t = map_funcs.frame_to_time(frame, FRAME_RATE)
    if frame <= FRAME_THRESHOLD:
        # Only use the tile_d_fits
        return (polynomial.polynomial_3_differential(t, *tile_d_fits['d'][0]),
                polynomial.polynomial_3_differential(t, *tile_d_fits['d+'][0]),
                polynomial.polynomial_3_differential(t, *tile_d_fits['d-'][0]))
    else:
        slab_v = (
            polynomial.polynomial_3(t, *slab_v_fits["v"][0]),
            polynomial.polynomial_3(t, *slab_v_fits["v+"][0]),
            polynomial.polynomial_3(t, *slab_v_fits["v-"][0]),
        )
        if frame > max(POSITIONS_FROM_TILES.keys()):
            # Only use the slab_v_fits
            return slab_v
        else:
            # Use both
            return (
                (polynomial.polynomial_3_differential(t, *tile_d_fits['d'][0]) + slab_v[0]) / 2.0,
                (polynomial.polynomial_3_differential(t, *tile_d_fits['d+'][0]) + slab_v[1]) / 2.0,
                (polynomial.polynomial_3_differential(t, *tile_d_fits['d-'][0]) + slab_v[2]) / 2.0,
            )


def _compute_acceleration(
        frame: int,
        tile_d_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]],
        slab_v_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]]) -> typing.Tuple[float, float, float]:
    """Returns acceleration by looking at frame to frame speed change."""
    v_0_triple: typing.Tuple[float, float, float] = _compute_speed(frame - 1, tile_d_fits, slab_v_fits)
    v_1_triple: typing.Tuple[float, float, float] = _compute_speed(frame + 1, tile_d_fits, slab_v_fits)
    ret = tuple(
        [(v1 - v0) / (2 / FRAME_RATE) for v0, v1 in zip(v_0_triple, v_1_triple)]
    )
    return ret


def _terminal_speed_and_mean_acceleration(
        v_initial: float, d_initial: float, dt: float, d_terminal: float
) -> typing.Tuple[float, float]:
    v_mean = (d_terminal - d_initial) / dt
    v_terminal = 2 * v_mean - v_initial
    if v_terminal < 0:
        raise ValueError(f'Negative terminal velocity of {v_terminal}')
    return v_terminal, (v_terminal - v_initial) / dt


def _quadratic_distance(d_0: float, v_0: float, a: float, t: float) -> float:
    return d_0 + v_0 * t + a * t**2 / 2.0


def _quadratic_distance_solution(d_0: float, v_0: float, a: float, d: float) -> typing.Tuple[float, float]:
    """
    Given an equation of the form: position = initial_position + initial_velocity * t + acceleration * t**2 / 2.0

    Using the quadratic equation: a * x**2 + b * x + c = 0

    And the solution:

    x = (-b ± math.sqrt(b**2 - 4 * a * c)) / (2 * a)

    Where:

    x = t
    a = acceleration / 2.0
    b = initial_velocity
    c = initial_position - position

    Thus:

    t = (-initial_velocity ± math.sqrt(initial_velocity**2 - 4 * acceleration / 2.0 * (initial_position - position))) / (2 * acceleration / 2.0)

    This returns the roots of t:

    t = (-v_0 ± sqrt(v_0**2 - 2 * a * (d_0 - d)) / a
    """
    part_two = math.sqrt(v_0**2 - 2 * a * (d_0 - d)) / a
    part_one = v_0 / a
    return part_one + part_two, part_one - part_two


def compute_impacts():
    """Does the calculation of de-acceleration after departure from the runway."""
    tile_d_fits = get_tile_d_fits()[1]
    slab_v_fits = get_slab_v_fits()
    d_data = _compute_distance(LAST_MEASURED_FRAME, tile_d_fits, slab_v_fits)
    v_data = _compute_speed(LAST_MEASURED_FRAME, tile_d_fits, slab_v_fits)
    dt = map_funcs.frames_to_dtime(LAST_MEASURED_FRAME, 1685, FRAME_RATE)
    d_fence = data.tiles.BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M
    print('Boundary fence impact:')
    boundary_fence_data = []
    for d, v in zip(d_data, v_data):
        try:
            v_terminal, accln = _terminal_speed_and_mean_acceleration(v, d, dt, d_fence)
            stop_in = v_terminal * (v_terminal / -accln) / 2.0
            print(f'Initial v={v:.1f} (m/s) d={d:.1f} (m)'
                  f' terminal v={v_terminal:.1f} (m/s) acceleration={accln:.1f} (m/s^2)'
                  f' stop={v_terminal / -accln:4.1f} (s)'
                  f' stop in ={stop_in:4.1f} (m)'
                  )
            boundary_fence_data.append((d, v, v_terminal, accln))
        except ValueError as err:
            print(f'Initial v={v:.1f} d={d:.1f} ERROR: {err}')
            boundary_fence_data.append((d, v, None, None))
    print(f'Final impact at fence +{data.tiles.FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M - data.tiles.BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M} (m):')
    for d, v, v_terminal, accln in boundary_fence_data:
        if v_terminal is not None and accln is not None:
            t = v_terminal / -accln
            dd = t * v_terminal / 2
            try:
                t_roots = _quadratic_distance_solution(
                    d_fence, v_terminal, accln,
                    data.tiles.FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M
                )
            except Exception:
                print('Not computable')
            else:
                # print('t_roots', t_roots)
                dt = -t_roots[1]
                v_final = v_terminal + accln * dt
                v_mean = (v_final + v_terminal) / 2.0
                d_final = v_mean * dt
                print(
                    f'Past boundary: dd={dd:6.1f} (m) dt={dt:3.1f} (s)'
                    f' v final={v_final:4.1f} (m/s) v mean={v_mean:4.1f} (m/s)'
                    f' d final={d_final:4.1f} (m)'
                )
        else:
            print(f'Past boundary: {None} (m)')


def print_events() -> None:
    tile_d_fits = get_tile_d_fits()[1]
    slab_v_fits = get_slab_v_fits()
    for frame_number in sorted(FRAME_EVENTS.keys()):
        t = map_funcs.frame_to_time(frame_number, FRAME_RATE)
        d, d_plus, d_minus = _compute_distance(frame_number, tile_d_fits, slab_v_fits)
        d_tol = max(abs(d - d_plus), abs(d - d_minus))
        v, v_plus, v_minus = _compute_speed(frame_number, tile_d_fits, slab_v_fits)
        v_tol = max(abs(v - v_plus), abs(v - v_minus))
        print(
            f'{frame_number:4d}',
            f'{t:4.1f}',
            f'{d:7.0f}±{d_tol:.0f} m',
            f'{v:7.1f}±{v_tol:.1f} m/s',
            f'{map_funcs.metres_per_second_to_knots(v):7.0f} ±{map_funcs.metres_per_second_to_knots(v_tol):.0f} knots',
            FRAME_EVENTS[frame_number]
        )


def print_table_of_events() -> None:
    tile_d_fits = get_tile_d_fits()[1]
    slab_v_fits = get_slab_v_fits()
    print('| Time (s) | Position (m) | Ground Speed (m/s, knots) | Acceleration (m/s^2 ) | Description |')
    print('| ---: | ---: | ---: | ---: | :--- |')
    for frame_number in sorted(FRAME_EVENTS.keys()):
        t = map_funcs.frame_to_time(frame_number, FRAME_RATE)
        d, d_plus, d_minus = _compute_distance(frame_number, tile_d_fits, slab_v_fits)
        d_tol = max(abs(d - d_plus), abs(d - d_minus))
        v, v_plus, v_minus = _compute_speed(frame_number, tile_d_fits, slab_v_fits)
        v_tol = max(abs(v - v_plus), abs(v - v_minus))
        a, a_plus, a_minus = _compute_acceleration(frame_number, tile_d_fits, slab_v_fits)
        a_tol = max(abs(a - a_plus), abs(a - a_minus))
        print(
            f'| {t:4.1f} |',
            f' {d:7.0f}±{d_tol:.0f} |',
            f' {v:7.1f}±{v_tol:.1f}, ',
            f' {map_funcs.metres_per_second_to_knots(v):.0f}±{map_funcs.metres_per_second_to_knots(v_tol):.0f} |',
            f' {a:7.1f}±{a_tol:.1f} |',
            f' {FRAME_EVENTS[frame_number]} |'
        )
    print('# Edit the above:')
    print('# Line 2: Remove -ve signe from acceleration.')
    print('# Line 3: Set position to 0, set acceleration to -0.7±0.1 (hand calculated).')
    print('# Line 9: change to | 56.1 |     ~1853 |     ~19, 37 |     ~ -3.9 |  Impact with fence |')
    print('# Line 9: | 57.0 |     ~1889 |    ~9, 18 |    N/A |  Final impact? |')
    print('# Line 10: remove.')


def main() -> int:
    print_events()
    print_table_of_events()
    compute_impacts()
    return 0


if __name__ == '__main__':
    sys.exit(main())
