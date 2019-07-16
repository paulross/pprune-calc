import math
import os
import subprocess
import sys
import typing

import numpy as np
from scipy.optimize import curve_fit

import map_data
import map_funcs
from common import polynomial


def print_calculated_data() -> None:
    print('Tile data:')
    print('TILE_OFFSETS:')
    for k in sorted(map_data.TILE_OFFSETS.keys()):
        print(f'{k} : {map_data.TILE_OFFSETS[k]}')
    print('THRESHOLD_ON_EACH_TILE:')
    for k in sorted(map_data.THRESHOLD_ON_EACH_TILE.keys()):
        print(f'{k:d} : {map_data.THRESHOLD_ON_EACH_TILE[k]}')
    print('TILE_EXTENDED_RUNWAY_LINE:')
    for k in sorted(map_data.TILE_EXTENDED_RUNWAY_LINE.keys()):
        print(f'{k:d} : {map_data.TILE_EXTENDED_RUNWAY_LINE[k]}')
    print('\nRunway data:')
    print(
        f'Runway length {map_data.RUNWAY_LENGTH_HEADING[0]:.1f} (m)'
        f', heading {map_data.RUNWAY_LENGTH_HEADING[1]:.1f} (degrees).'
    )
    print(
        f'Runway width {map_data.RUNWAY_WIDTH_PX:.1f} (pixels)'
        f', {map_data.TILE_SCALE_M_PER_PIXEL * map_data.RUNWAY_WIDTH_PX:.1f} (m).'
    )
    print(f'Boundary fence from threshold: {map_data.BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M:.1f} (m)')
    print(f'Final building from threshold: {map_data.FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M:.1f} (m)')


def create_distance_array_of_tile_data() -> typing.Dict[str, np.ndarray]:
    """Returns a numpy array of time, position from the tile position data."""
    columns = ('Frame', 'Time', 'd', 'd+', 'd-')
    ret = {k: np.empty((len(map_data.POSITIONS_FROM_TILES), 1)) for k in columns}
    for f, frame_number in enumerate(sorted(map_data.POSITIONS_FROM_TILES.keys())):
        t = map_funcs.frame_to_time(frame_number)
        dx = map_data.POSITIONS_FROM_TILES[frame_number][1].x - map_data.THRESHOLD_ON_EACH_TILE[map_data.POSITIONS_FROM_TILES[frame_number][0]].x
        dy = map_data.POSITIONS_FROM_TILES[frame_number][1].y - map_data.THRESHOLD_ON_EACH_TILE[map_data.POSITIONS_FROM_TILES[frame_number][0]].y
        d_threshold = map_data.TILE_SCALE_M_PER_PIXEL * math.sqrt(dx**2 + dy**2)
        if frame_number < map_data.FRAME_THRESHOLD:
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
        v_name: curve_fit(polynomial.polynomial_3, map_data.SLAB_SPEEDS[:, 1], map_data.SLAB_SPEEDS[:, v + 2])
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

    THRESHOLD_TIME = map_funcs.frame_to_time(map_data.FRAME_THRESHOLD)
    d_offsets = [
        polynomial.polynomial_3_integral(THRESHOLD_TIME, *v_fits["v"][0]),
        polynomial.polynomial_3_integral(THRESHOLD_TIME, *v_fits["v+"][0]),
        polynomial.polynomial_3_integral(THRESHOLD_TIME, *v_fits["v-"][0]),
    ]
    stream.write(f'# d_offsets {d_offsets}\n')
    stream.write(f'# Columns: frame, t, v, v+, v- (m/s), d, d+, d-, a, a+, a-, v, v+, v- (knots)\n')
    for i in range(len(map_data.SLAB_SPEEDS)):
        t = map_data.SLAB_SPEEDS[i, 1]
        v_m_per_second = [map_data.SLAB_SPEEDS[i, j] for j in (2, 3, 4)]
        v_knots = [map_funcs.metres_per_second_to_knots(v) for v in v_m_per_second]
        row = [
            f'{map_data.SLAB_SPEEDS[i, 0]:<6.0f}',
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


def plot_all(directory: str) -> None:
    for file_name in os.listdir(directory):
        if os.path.splitext(file_name)[1] == '.plt':
            print(f'Plotting "{file_name}"')
            proc = subprocess.Popen(
                args=['gnuplot', '-p', file_name],
                shell=False,
                cwd=directory,
            )
            try:
                outs, errs = proc.communicate(timeout=1)
            except subprocess.TimeoutExpired as err:
                print('ERROR:', err)
                proc.kill()
                outs, errs = proc.communicate()


def _compute_distance(
        frame: int,
        tile_d_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]],
        slab_v_fits: typing.Dict[str, typing.Tuple[np.ndarray, np.ndarray]]) -> typing.Tuple[float, float, float]:
    t = map_funcs.frame_to_time(frame)
    if frame <= map_data.FRAME_THRESHOLD:
        # Only use the tile_d_fits
        return (polynomial.polynomial_3(t, *tile_d_fits['d'][0]),
                polynomial.polynomial_3(t, *tile_d_fits['d+'][0]),
                polynomial.polynomial_3(t, *tile_d_fits['d-'][0]))
    else:
        THRESHOLD_TIME = map_funcs.frame_to_time(map_data.FRAME_THRESHOLD)
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
        if frame > max(map_data.POSITIONS_FROM_TILES.keys()):
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
    t = map_funcs.frame_to_time(frame)
    if frame <= map_data.FRAME_THRESHOLD:
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
        if frame > max(map_data.POSITIONS_FROM_TILES.keys()):
            # Only use the slab_v_fits
            return slab_v
        else:
            # Use both
            return (
                (polynomial.polynomial_3_differential(t, *tile_d_fits['d'][0]) + slab_v[0]) / 2.0,
                (polynomial.polynomial_3_differential(t, *tile_d_fits['d+'][0]) + slab_v[1]) / 2.0,
                (polynomial.polynomial_3_differential(t, *tile_d_fits['d-'][0]) + slab_v[2]) / 2.0,
            )


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
    d_data = _compute_distance(map_data.LAST_MEASURED_FRAME, tile_d_fits, slab_v_fits)
    v_data = _compute_speed(map_data.LAST_MEASURED_FRAME, tile_d_fits, slab_v_fits)
    dt = map_funcs.frames_to_dtime(map_data.LAST_MEASURED_FRAME, 1685)
    d_fence = map_data.BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M
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
    print(f'Final impact at fence +{map_data.FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M - map_data.BOUNDARY_FENCE_DISTANCE_FROM_THRESHOLD_M} (m):')
    for d, v, v_terminal, accln in boundary_fence_data:
        if v_terminal is not None and accln is not None:
            t = v_terminal / -accln
            dd = t * v_terminal / 2
            try:
                t_roots = _quadratic_distance_solution(
                    d_fence, v_terminal, accln, map_data.FINAL_BUILDING_DISTANCE_FROM_THRESHOLD_M
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
    for frame_number in sorted(map_data.FRAME_EVENTS.keys()):
        t = map_funcs.frame_to_time(frame_number)
        d, d_plus, d_minus = _compute_distance(frame_number, tile_d_fits, slab_v_fits)
        d_tol = max(abs(d - d_plus), abs(d - d_minus))
        v, v_plus, v_minus = _compute_speed(frame_number, tile_d_fits, slab_v_fits)
        v_tol = max(abs(v - v_plus), abs(v - v_minus))
        print(
            f'{frame_number:4d}',
            f'{t:4.1f}',
            f'{d:7.0f} ±{d_tol:.0f} m',
            f'{v:7.1f} ±{v_tol:.1f} m/s',
            f'{map_funcs.metres_per_second_to_knots(v):7.0f} ±{map_funcs.metres_per_second_to_knots(v_tol):.0f} knots',
            map_data.FRAME_EVENTS[frame_number]
        )


def main():
    print_calculated_data()
    with open('plots/tile_distance_data.dat', 'w') as ostream:
        print('Writing tile results...')
        write_tile_results(ostream)
    with open('plots/slab_speed_data.dat', 'w') as ostream:
        print('Writing slab results...')
        write_slab_results(ostream)
    plot_dir = os.path.join(os.path.dirname(__file__), 'plots')
    print(f'Looking for plot files in "{plot_dir}"')
    plot_all(plot_dir)
    print_events()
    compute_impacts()
    return 0


if __name__ == '__main__':
    sys.exit(main())
