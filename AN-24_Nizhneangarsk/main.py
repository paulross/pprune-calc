"""
Discussion: https://www.pprune.org/rumours-news/622950-angara-airlines-24-landing-accident-nizhneangarsk.html

Video: https://youtu.be/LtJcgdU5MUk

Data from google maps and OpenStreetMap

Accident: https://en.wikipedia.org/wiki/Angara_Airlines_Flight_200

Nizhneangarsk Airport
---------------------
Airport location (https://en.wikipedia.org/wiki/Nizhneangarsk_Airport): 55°48′6″N 109°35′12″E
That is 55.80166666666666, 109.58666666666666

IATA: none ICAO: UIUN
Runway is 04/22, 1653m long

Threshold of 22 on google maps: https://www.google.com/maps/@55.807288,109.6034312,757m/data=!3m1!1e3

RT videos: https://www.rt.com/news/462775-russia-nizhneangarsk-crash-landing/

"""
import os
import subprocess
import sys
import typing

import numpy as np
from scipy.optimize import curve_fit

import data.tiles
import data.video_a
import data.video_b
import data.video_ab
import map_funcs
from cmn import polynomial


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


#======== Video B ========
def _get_video_b_v_array() -> np.ndarray:
    """Returns an array of the speed and plus, minus from video B on a timebase of video A."""
    x_array = data.video_b.aircraft_x_array()
    x_fits = list(
        curve_fit(polynomial.polynomial_3, x_array[:, 0], x_array[:, i])[0]
        for i in range(1, 4)
    )
    v_array = np.empty_like(x_array)
    v_array[:, 0] = x_array[:, 0] + data.video_ab.time_difference_mid_max_min().mid
    # print(x_fits)
    for row in range(len(x_array)):
        v_array[row, 1] = polynomial.polynomial_3_differential(x_array[row, 0], *x_fits[0])
        v_array[row, 2] = polynomial.polynomial_3_differential(x_array[row, 0], *x_fits[1])
        v_array[row, 3] = polynomial.polynomial_3_differential(x_array[row, 0], *x_fits[2])
    return v_array


def write_video_b_results(stream: typing.TextIO=sys.stdout):
    # x_array is in video B time
    x_array = data.video_b.aircraft_x_array()
    # v_array is in video A time
    v_array = _get_video_b_v_array()
    stream.write(f'# Columns: t, d, d+, d-, v, v+, v- (m/s), v, v+, v- (knots)\n')
    for i in range(len(v_array)):
        t = v_array[i, 0]
        row = [
            f'{t:<6.2f}',
        ]
        row.extend([f'{v:8.1f}' for v in x_array[i, 1:]])
        row.extend([f'{v:8.1f}' for v in v_array[i, 1:]])
        row.extend([f'{map_funcs.metres_per_second_to_knots(v):8.1f}' for v in v_array[i, 1:]])
        stream.write(' '.join((row)))
        stream.write('\n')
#======== END: Video B ========


def main() -> int:
    with open('plots/tile_distance_data.dat', 'w') as ostream:
        print('Writing data.video_a tile results...')
        data.video_a.write_tile_results(ostream)
    with open('plots/slab_speed_data.dat', 'w') as ostream:
        print('Writing data.video_a slab results...')
        data.video_a.write_slab_results(ostream)
    with open('plots/video_b.dat', 'w') as ostream:
        print('Writing video B results...')
        write_video_b_results(ostream)
    plot_dir = os.path.join(os.path.dirname(__file__), 'plots')
    print(f'Looking for plot files in "{plot_dir}"')
    plot_all(plot_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
