"""
Plots video data.
"""
import os
import sys
import typing

from analysis import video_data

PLOT_DIRECTORY = 'plots'


def plot_filepath(name: str) -> str:
    """Return a path to a file."""
    plot_dir: str = os.path.join(os.path.dirname(__file__), PLOT_DIRECTORY)
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    return os.path.join(plot_dir, name)


def print_gnuplot(func: typing.Callable,
                  slc: slice,
                  title: str,
                  notes: typing.Tuple[str],
                  stream=sys.stdout) -> None:
    """Print gnuplot data suitable for plotting with xyerrorbars.

    Example of invocation in gnuplot::

        plot "data" using 1:2:3:4:5:6 w xyerrorbars # ( x, y, xlow, xhigh, ylow, yhigh )
    """
    stream.write('# "{}"\n'.format(title))
    if len(notes):
        stream.write('#\n# Notes\n')
    for note in notes:
        stream.write('# {}\n'.format(note))
    stream.write('# {:>2} {:>8} {:>8} {:>8} {:>8} {:>8}\n'.format(
            't', 'y', 't_low', 't_high', 'y_low', 'y_high'
        )
    )
    for t in range(slc.start, slc.stop, slc.step):
        stream.write('{:<4d} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}\n'.format(
                t,
                func(t, 0),
                t - video_data.ERROR_TIMESTAMP,
                t + video_data.ERROR_TIMESTAMP,
                func(t, -1),
                func(t, 1),
            )
        )

def create_plots():
    # Scan for .plt files and call gnuplot on them.
    pass


