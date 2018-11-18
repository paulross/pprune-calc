import sys
import typing

import numpy as np

from analysis import plot_common
from analysis import plot_constants
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils


def gnuplot_ground_speed(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    gs_arrays = [
        video_analysis.ground_speeds(min_max) for min_max in list(video_data.ErrorDirection)
    ]
    gs_fits = [plot_common.get_gs_fit(err) for err in video_data.ErrorDirection]
    result = [
        '# "{}"'.format('Grounds speed, mid data and smoothed data.')
    ]
    notes = [
        'Columns:',
        '1: Time (s)',
        '2: Ground speed (knots)',
        '3: Time with error -ve (s)',
        '4: Time with error +ve (s)',
        '5: Ground speed with error -ve (knots)',
        '6: Ground speed with error +ve (knots)',
        '7: Ground speed fitted (knots)',
        '8: Ground speed fitted with error -ve (knots)',
        '9: Ground speed fitted with error +ve (knots)',
    ]
    if len(notes):
        result.append('#')
        result.append('# Notes:')
    for note in notes:
        result.append('# {}'.format(note))
    timebase = gs_arrays[0][:,0]
    FORMAT = '{:8.3f}'
    factor = video_utils.m_p_s_to_knots(1.0)
    for i in range(len(timebase)):
        t = timebase[i]
        part_line = [
            '{:.1f}'.format(t)
        ]
        # Original data ane error estimates.
        part_line.append(FORMAT.format(gs_arrays[1][i, 1] * factor))
        part_line.append(FORMAT.format(t - video_data.ERROR_TIMESTAMP))
        part_line.append(FORMAT.format(t + video_data.ERROR_TIMESTAMP))
        part_line.append(FORMAT.format(gs_arrays[0][i, 1] * factor))
        part_line.append(FORMAT.format(gs_arrays[2][i, 1] * factor))
        # Fitted lines
        part_line.append(FORMAT.format(video_analysis.ground_speed_from_fit(t, gs_fits[1]) * factor))
        part_line.append(FORMAT.format(video_analysis.ground_speed_from_fit(t, gs_fits[0]) * factor))
        part_line.append(FORMAT.format(video_analysis.ground_speed_from_fit(t, gs_fits[2]) * factor))
        # print(part_line)
        result.append(' '.join(part_line))
    stream.write('\n'.join(result))
    return []


def gnuplot_ground_speed_plt() -> str:
    return """# set logscale x
set colorsequence classic
set grid
set title "Ground Speed."
set xlabel "Video Time (seconds)"
set xtics
#set format x ""

# set logscale y
set ylabel "Ground Speed (knots)"
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
plot "{file_name}.dat" using 1:2:3:4:5:6 title "Raw data" w xyerrorbars, \\
    "{file_name}.dat" using 1:7 title "Fitted to mid values" lw 2 w line

#    "{file_name}.dat" using 1:8 title "Fitted to extreme minimum values" lw 1 w line, \\
#    "{file_name}.dat" using 1:9 title "Fitted to extreme maximum values" lw 1 w line
reset
"""


def gnuplot_ground_speed_extrapolated(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    gs_arrays = [
        video_analysis.ground_speeds(min_max) for min_max in list(video_data.ErrorDirection)
    ]
    gs_fits = [plot_common.get_gs_fit(err) for err in video_data.ErrorDirection]
    result = [
        '# "{}"'.format('Grounds speed, mid data and smoothed data, extrapolated.')
    ]
    notes = [
        'Columns',
        '1: Time (s)',
        '2: Ground speed, mid values (knots).',
        '3: Time, minimum (s).',
        '4: Time, maximum (s).',
        '5: Ground speed, min values (knots).',
        '6: Ground speed, max values (knots).',
        '7: Ground speed extrapolated, mid values (knots).',
        '8: Ground speed extrapolated, min values (knots).',
        '9: Ground speed extrapolated, max values (knots).',
    ]
    if len(notes):
        result.append('#')
        result.append('# Notes:')
        for note in notes:
            result.append('# {}'.format(note))
    gs_arrays_extrapolated = []
    for fit in gs_fits:
        gs_arrays_extrapolated.append(
            np.array(
                [(t, video_analysis.ground_speed_from_fit(t, fit)) for t in plot_constants.EXTRAPOLATED_RANGE]
            )
        )
    # Convert selected columns to knots
    k = video_utils.m_p_s_to_knots(1.0)
    for i in range(3):
        gs_arrays[i][:, 1] *= k
        gs_arrays_extrapolated[i][:, 1] *= k

    stream.write('\n'.join(result))
    stream.write('\n')
    plot_common.gnuplot_write_arrays(
        stream,
        gs_arrays[1],
        np.column_stack((gs_arrays[1][:,0], gs_arrays[1][:,0] - video_data.ERROR_TIMESTAMP)),
        np.column_stack((gs_arrays[1][:,0], gs_arrays[1][:,0] + video_data.ERROR_TIMESTAMP)),
        gs_arrays[0],
        gs_arrays[2],
        gs_arrays_extrapolated[1],
        gs_arrays_extrapolated[0],
        gs_arrays_extrapolated[2],
    )
    # Print time for v=0
    plot_data = []
    for i in range(len(gs_arrays_extrapolated)):
        t = video_utils.interpolate(gs_arrays_extrapolated[i][:, 1], gs_arrays_extrapolated[i][:, 0], 0.0)
        print('Time start[{:d}] t, v=0: {:.3f} Polynomial roots: {}'.format(i, t, np.roots(list(reversed(gs_fits[i])))))
        plot_data.append(
            'set arrow from {t:.3f},{offset:d} to {t:.3f},{zero:.3f} lt {lt:d}'.format(
                t=t,
                offset=50 + i * 25,
                zero=0.0,
                lt=i + 1,
            )
        )
        plot_data.append(
            'set label "t={t0:.1f}s" at {t1:.1f},{offset:d} left font ",12"'.format(
                t0=t,
                t1=t-2,
                offset=54 + i * 25,
            )
        )
    return plot_data


def gnuplot_ground_speed_extrapolated_plt() -> str:
    return """# set logscale x
set colorsequence classic
set grid
set title "Ground Speed."
set xlabel "Video Time (seconds)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Ground Speed (knots)"
# set yrange [-25:125]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "{file_name}.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

{computed_data}

# linespoints
plot "{file_name}.dat" using 1:2:3:4:5:6 title "Raw data" w xyerrorbars, \\
    "{file_name}.dat" using 1:7 title "Fitted to mid values" lt 2 lw 2 w lines, \\
    "{file_name}.dat" using 1:8 title "-10 knots" lt 1 lw 0.5 w lines, \\
    "{file_name}.dat" using 1:9 title "+10 knots" lt 3 lw 0.5 w lines
reset
"""