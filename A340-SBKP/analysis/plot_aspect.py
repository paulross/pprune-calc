import sys
import typing

import numpy as np

from analysis import aspect
from analysis import plot_common
from analysis import video_data


def gnuplot_aspect(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    arrays_from_transits = {
        min_max: aspect.aspects(min_max) for min_max in list(video_data.ErrorDirection)
    }
    timebase = arrays_from_transits[video_data.ErrorDirection.MID][:, 0]
    aspect_from_transits_with_errors = np.column_stack(
        (
            timebase,
            arrays_from_transits[video_data.ErrorDirection.MID][:, 1],
            arrays_from_transits[video_data.ErrorDirection.MIN][:, 0],
            arrays_from_transits[video_data.ErrorDirection.MAX][:, 0],
            arrays_from_transits[video_data.ErrorDirection.MIN][:, 1],
            arrays_from_transits[video_data.ErrorDirection.MAX][:, 1],
        )
    )
    aspect_from_transits_fitted = aspect.aspect_fitted_line()
    arrays_from_wing_tips = {
        min_max: aspect.aspects_from_wing_tips(min_max) for min_max in list(video_data.ErrorDirection)
    }
    timebase_from_wing_tips = arrays_from_wing_tips[video_data.ErrorDirection.MID][:, 0]
    aspect_from_wing_tips_with_errors = np.column_stack(
        (
            timebase_from_wing_tips,
            arrays_from_wing_tips[video_data.ErrorDirection.MID][:, 1],
            arrays_from_wing_tips[video_data.ErrorDirection.MIN][:, 0],
            arrays_from_wing_tips[video_data.ErrorDirection.MAX][:, 0],
            arrays_from_wing_tips[video_data.ErrorDirection.MIN][:, 1],
            arrays_from_wing_tips[video_data.ErrorDirection.MAX][:, 1],
        )
    )
    aspect_fitted_from_wing_tips = aspect.aspect_from_wing_tips_fitted_line()
    # TODO: Make use of notes the same in all functions
    notes = [
        '"{}"'.format('Aspects, errors, and polynomial fit.'),
        'Columns:',
        '1: time (s)',
        '2: aspect_from_transits (deg)',
        '3: -dt',
        '4: +dt',
        '5: -dy (deg)',
        '6: +dy (deg)',
        '7: aspect_from_transit_fit (deg)',
        '8: aspect_from_wingtips (deg)',
        '9: -dt',
        '10: +dt',
        '11: -dy (deg)',
        '12: +dy (deg)',
        '13: aspect_from_wingtips_fit (deg)',
    ]
    if len(notes):
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))
    plot_common.gnuplot_write_arrays(
        stream,
        aspect_from_transits_with_errors,
        aspect_from_transits_fitted,
        aspect_from_wing_tips_with_errors,
        aspect_fitted_from_wing_tips,
    )
    return []


def gnuplot_aspect_plt() -> str:
    return """# set logscale x
set grid
set title "Bearings to Observer."
set xlabel "Time (s)"
set mxtics 5
#set xrange [0:3000]
#set xtics
#set format x ""

# set logscale y
set ylabel "Bearing (degrees)"
#set yrange [100:-1000]
set ytics 20
set mytics 2
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

set terminal svg size 1000,500           # choose the file format

# set key off

set output "{file_name}.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# fit_aspect(x) = a + b*x + c*x**2 + d*x**3
# fit fit_aspect(x) "{file_name}.dat" using 1:2 via a,b,c,d

plot "{file_name}.dat" using 1:2:3:4:5:6 title "Transit data" lt 1 w xyerrorbars, \\
    "{file_name}.dat" using 1:7 title "Transit fit" lw 2 lt 1 w lines smooth bezier, \\
    "{file_name}.dat" using 1:8:9:10:11:12 title "Wing tip data" lt 2 w boxxyerror, \\
    "{file_name}.dat" using 1:13 title "Wing tip fit" lw 2 lt 2 w lines smooth bezier

reset
"""