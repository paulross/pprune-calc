import math
import sys
import typing

import numpy as np

from analysis import plot_common
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils


def gnuplot_acceleration(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    gs_fits = plot_common.get_gs_fits()
    # print('TRACE: gs_fits', gs_fits)
    # print(
    #     'Acceleration at t=0 (knots/s):',
    #     video_utils.m_p_s_to_knots(video_analysis.ground_speed_differential(-33.0, gs_fits[1])),
    # )
    timebase = video_analysis.ground_speed_timebase()
    accl_arrays_smoothed = []
    for fit in gs_fits:
        accl_arrays_smoothed.append(
            np.array(
                [(t, video_analysis.ground_speed_differential(t, fit)) for t in timebase]
            )
        )
    result = [
        '# "{}"'.format('Acceleration (m/s**2.')
    ]
    notes = [
    ]
    if len(notes):
        result.append('#')
        result.append('# Notes:')
    for note in notes:
        result.append('# {}'.format(note))
        result.append('# {:>2} {:>8} {:>8}'.format(
            't', 'speed', 'smoothed'
        )
        )
    timebase = accl_arrays_smoothed[0][:,0]
    FORMAT = '{:8.3f}'
    # Convert selected columns to knots/s
    k = video_utils.m_p_s_to_knots(1.0)
    for i in range(len(timebase)):
        t = timebase[i]
        part_line = [
            '{:.1f}'.format(t),
            FORMAT.format(k * accl_arrays_smoothed[1][i, 1]),
            FORMAT.format(k * accl_arrays_smoothed[0][i, 1]),
            FORMAT.format(k * accl_arrays_smoothed[2][i, 1]),
        ]
        result.append(' '.join(part_line))
    stream.write('\n'.join(result))
    return []


def gnuplot_acceleration_plt() -> str:
    return """# set logscale x
set grid
set title "Acceleration."
set xlabel "Video Time (seconds)"
set xtics
#set format x ""

# set logscale y
set ylabel "Acceleration (knots/s)"
# set yrange [:110]
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

set terminal svg size 700,500           # choose the file format

set output "{file_name}.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# linespoints
plot "{file_name}.dat" using 1:2 title "Acceleration from best fit of ground speed" lt 2 lw 2 w lines
#    "{file_name}.dat" using 1:3 title "Acceleration (Min)" lw 2 w lines, \\
#    "{file_name}.dat" using 1:4 title "Acceleration (Max)" lw 2 w lines
reset
"""


def gnuplot_raw_acceleration(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    has_prev = False
    t_prev = math.nan
    gs_prev: float = math.nan
    gs_min_prev: float = math.nan
    gs_max_prev: float = math.nan
    plot_data = []
    for transit in video_data.AIRCRAFT_TRANSITS:
        t = transit.time
        dt = transit.dt
        gs = video_utils.m_p_s_to_knots(video_analysis.ground_speed_raw(t, dt, 0))
        gs_min = video_utils.m_p_s_to_knots(video_analysis.ground_speed_raw(t, dt, -1))
        gs_max = video_utils.m_p_s_to_knots(video_analysis.ground_speed_raw(t, dt, 1))
        if has_prev:
            plot_data.append(
                [
                    t,
                    (gs - gs_prev) / (t - t_prev),
                    t - video_data.ERROR_TIMESTAMP,
                    t + video_data.ERROR_TIMESTAMP,
                    # TODO: Is this right or should we cross min/max
                    # TODO: Add variation in dt
                    # (gs_min - gs_max_prev) / (t - t_prev),
                    # (gs_max - gs_min_prev) / (t - t_prev),
                    (gs_min - gs_min_prev) / (t - t_prev),
                    (gs_max - gs_max_prev) / (t - t_prev),
                ]
            )
        t_prev = t
        gs_prev = gs
        gs_min_prev = gs_min
        gs_max_prev = gs_max
        has_prev = True
    stream.write('# "{}"\n'.format('Raw acceleration in Knots/s with error estimate.'))
    notes = [
    ]
    if len(notes):
        stream.write('#\n# Notes:\n')
    for note in notes:
        stream.write('# {}\n'.format(note))
    stream.write('# {:>2} {:>8} {:>8} {:>8} {:>8} {:>8}\n'.format(
            't', 'accn', 't_low', 't_high', 'accn_low', 'accn_high'
        )
    )
    for data in plot_data:
        stream.write('{:.1f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}\n'.format(*data)
        )
    return []