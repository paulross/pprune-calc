import os
import subprocess
import sys
import typing

import numpy as np

from analysis import plot_constants
from analysis import video_analysis


def gnuplot_write_arrays(stream: typing.TextIO=sys.stdout,
                         *args: np.ndarray) -> None:
    # Requires arg[:, 0] to be ordered.
    times = set()
    for arg in args:
        if arg.ndim != 2:
            raise ValueError('Arrays must be 2D not shape: {}'.format(arg.shape))
        times |= set(arg[:,0])
    timebase = sorted(times)
    indices = [0,] * len(args)
    for t in timebase:
        part_line = [
            '{:<8.1f}'.format(t)
        ]
        for i_arg, arg in enumerate(args):
            i = indices[i_arg]
            if i < len(arg) and arg[i, 0] == t:
                part_line.extend(
                    ['{:8.3f}'.format(arg[i, j]) for j in range(1, arg.shape[1])]
                )
                indices[i_arg] += 1
            else:
                part_line.extend(
                    ['{:8s}'.format('NaN') for j in range(1, arg.shape[1])]
                )
        stream.write(' '.join(part_line))
        stream.write('\n')


def get_gs_fits() -> typing.List[typing.List[float]]:
    """
    Returns a list of polynomial fits to ground speed.
    [0] - Min error ground speed.
    [1] - Mid ground speed.
    [2] - Max error ground speed.
    """
    # # Using a fit to extreme values with ErrorDirection. This gives some bad extrapolations.
    # gs_fits = [
    #     video_analysis.ground_speed_curve_fit(e) for e in list(video_data.ErrorDirection)
    # ]
    # Using Offset
    gs_fits = [
        video_analysis.ground_speed_curve_fit_with_offset(e) for e in plot_constants.GROUND_SPEED_OFFSETS
    ]
    return gs_fits


def plot_file(name: str) -> str:
    if name == '':
        return os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, 'plots'))
    return os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, 'plots', name))


def write_dat_plt_call(name: str, fn_dat: typing.Callable, fn_plt: typing.Callable) -> None:
    """
    Create the plot for name.
    fn_data is a function that takes a stream and writes the 'name.dat' file. This must return
    a list of strings, if non-empty then they are written into the plt file as {computed_data}.
    fn_plot is a function that return the 'name.plt' string ready to insert the 'name.dat'
    into the format variable 'file_name'.
    """
    print('Writing "{}"'.format(name))
    with open(plot_file('{}.dat'.format(name)), 'w') as outfile:
        computed_data_strings = fn_dat(outfile)
    if len(computed_data_strings):
        plot_data = fn_plt().format(
            file_name=name, computed_data='\n'.join(computed_data_strings)
        )
    else:
        plot_data = fn_plt().format(file_name=name)
    plt_file_path = plot_file('{}.plt'.format(name))
    with open(plt_file_path, 'w') as outfile:
        outfile.write(plot_data)
    proc = subprocess.Popen(
        args=['gnuplot', '-p', os.path.basename(plt_file_path)],
        shell=False,
        cwd=os.path.dirname(plt_file_path),
    )
    try:
        outs, errs = proc.communicate(timeout=1)
    except subprocess.TimeoutExpired as err:
        print('ERROR:', err)
        proc.kill()
        outs, errs = proc.communicate()
    # print(outs, errs, proc.returncode)
