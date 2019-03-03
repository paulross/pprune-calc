import math
import sys
import typing

import numpy as np

from analysis import plot_common
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils


def gnuplot_acceleration(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    timebase = video_analysis.ground_speed_timebase()
    accl_arrays_smoothed = []
    for err in video_data.ErrorDirection:
        fit = plot_common.get_gs_fit(err)
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
set colorsequence classic
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

def markdown_table_acceleration_error() -> typing.Tuple[typing.List[str], str]:
    return _markdown_table_acceleration_error(False)


def markdown_table_acceleration_error_worst_case() -> typing.Tuple[typing.List[str], str]:
    return _markdown_table_acceleration_error(True)


def _markdown_table_acceleration_error(worst_cast: bool) -> typing.Tuple[typing.List[str], str]:
    """
    Returns a markdown table and a title for the acceleration error.
    """
    gs_fits = [plot_common.get_gs_fit(err) for err in video_data.ErrorDirection]
    three_dist_arrays = plot_common.get_distances_min_mid_max(video_data.TIME_VIDEO_END_ASPHALT.time)
    # Time ranges for min/mid/max of start of take off
    t_range = [arr[0][0] for arr in three_dist_arrays]
    # Distance of start of take off from start of runway for min/mid/max
    d_range = [arr[0][1] for arr in three_dist_arrays]
    accl_mid = video_utils.m_p_s_to_knots(
        video_analysis.ground_speed_from_fit(
            video_data.TIME_VIDEO_END_ASPHALT.time, gs_fits[1]
        )
    ) / (video_data.TIME_VIDEO_END_ASPHALT.time - t_range[1])

    table = [
        '| {} |'.format(
            ' | '.join(
                [
                    'Speed Error',
                    'Time from start take off to end asphalt (s)',
                    'Speed (knots)',
                    'Mean Acceleration (knots/s)',
                    'Error (knots/s)',
                    'Distance from start take off from start of runway (m)',
                ]
            )
        ),
        '| --- | ---: | ---: | ---: | ---: | ---: |',
    ]
    err = -10
    for i in range(len(gs_fits)):
        v_m_per_sec = video_analysis.ground_speed_from_fit(
            video_data.TIME_VIDEO_END_ASPHALT.time, gs_fits[i]
        )
        if worst_cast:
            t_take_off = video_data.TIME_VIDEO_END_ASPHALT.time - t_range[2 - i]
            # FIXME: How is the worst case calculation been done?
            # Hand calculation gives start of take off distances of 542, 511, 485m.
            # How was this result obtained?
            d_start = video_data.RUNWAY_LEN_M - (t_take_off * v_m_per_sec / 2.0)
        else:
            t_take_off = video_data.TIME_VIDEO_END_ASPHALT.time - t_range[i]
            d_start = d_range[i]
        v_knots = video_utils.m_p_s_to_knots(v_m_per_sec)
        a = v_knots / t_take_off
        table.append(
            '| {:d} knots | {:.1f} | {:.0f} | {:.2f} | {:.2f} | {:.0f} |'.format(
                err, t_take_off, v_knots, a, a - accl_mid, d_start
            )
        )
        err += 10
    if worst_cast:
        title = 'Acceleration error, worst case.'
    else:
        title = 'Acceleration error.'
    return table, title
