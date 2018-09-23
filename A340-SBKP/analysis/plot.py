"""
Plots video data.
"""
import math
import os
import sys
import typing

from analysis import video_data
from analysis import video_analysis

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
        stream.write('#\n# Notes:\n')
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


PLT_SPEED = """set logscale x
set grid
set title "{title}."
set xlabel "Time (seconds)"
set xtics
#set format x ""

# set logscale y
set ylabel "Speed (Knots)."
# set yrange [8:35]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

# Curve fit
#cost(x) = a + (b / (x/1024))
#fit cost(x) "{file_name}.dat" using 1:2 via a,b

set terminal svg size 750,550           # choose the file format

set output "{file_name}.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

plot "{file_name}.svg" using 1:2:3:4:5:6 w xyerrorbars # ( x, y, xlow, xhigh, ylow, yhigh )
reset

"""


def gnuplot_raw_transits(stream: typing.TextIO=sys.stdout) -> None:
    plot_data = []
    for transit in video_data.AIRCRAFT_TRANSITS:
        t = transit.time
        dt = transit.dt
        plot_data.append(
            [
                t,
                video_analysis.m_p_s_to_knots(video_analysis.ground_speed_raw(t, dt, 0)),
                t - video_data.ERROR_TIMESTAMP,
                t + video_data.ERROR_TIMESTAMP,
                video_analysis.m_p_s_to_knots(video_analysis.ground_speed_raw(t, dt, -1)),
                video_analysis.m_p_s_to_knots(video_analysis.ground_speed_raw(t, dt, 1)),
            ]
        )
    stream.write('# "{}"\n'.format('Raw transits in Knots with error estimate.'))
    notes = [
    ]
    if len(notes):
        stream.write('#\n# Notes:\n')
    for note in notes:
        stream.write('# {}\n'.format(note))
    stream.write('# {:>2} {:>8} {:>8} {:>8} {:>8} {:>8}\n'.format(
            't', 'speed', 't_low', 't_high', 'speed_low', 'speed_high'
        )
    )
    for data in plot_data:
        stream.write('{:.1f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}\n'.format(*data)
        )


def create_plots():
    # Scan for .plt files and call gnuplot on them.
    pass


def main():
    gnuplot_raw_transits()

    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
