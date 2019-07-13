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


def get_tile_d_fits() -> typing.Dict[str, np.ndarray]:
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
    array_dict, fits = get_tile_d_fits()
    # print('fits', fits)
    # Differentiate for velocity.
    stream.write('# Tile distance data\n')
    for d in TILE_D_ORDER:
        # coeff_str = [f'{v:.3e}' for v in fits[d][0]]
        # stream.write(f'# {d} coefficients: {", ".join(coeff_str)}\n')
        formulae = polynomial.polynomial_string(D_FORMULAE[d], 't', '.3e', *fits[d][0])
        stream.write(f'# {formulae}\n')
    # stream.write(f'# d+ coefficients {fits["d+"][0]}\n')
    # stream.write(f'# d- coefficients {fits["d-"][0]}\n')
    stream.write(f'# Columns: frame, t, d, d+, d-, v, v+, v- (m/s), v, v+, v- (knots)\n')
    for i in range(len(array_dict['Frame'])):
        t = array_dict['Time'][i, 0]
        v_m_per_second = [polynomial.polynomial_3_differential(t, *fits[k][0]) for k in TILE_D_ORDER]
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


def get_slab_v_fits() -> typing.Dict[str, np.ndarray]:
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
    return 0


if __name__ == '__main__':
    sys.exit(main())
