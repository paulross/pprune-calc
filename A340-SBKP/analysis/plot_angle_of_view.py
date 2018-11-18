import sys
import typing

import numpy as np

from analysis import aspect, video_analysis, plot_constants
from analysis import plot_common
from analysis import video_data


def gnuplot_angle_of_view(stream: typing.TextIO=sys.stdout) -> typing.List[str]:



    for raw_aspect in video_data.AIRCRAFT_ASPECTS_FROM_WING_TIPS:
        t = raw_aspect.video_time
        px_len = raw_aspect.length
        px_span = raw_aspect.span


    arrays_from_wing_tips = {
        min_max: aspect.aspects_from_wing_tips(min_max) for min_max in list(video_data.ErrorDirection)
    }
    # raw_data = video_data.AIRCRAFT_ASPECTS_FROM_WING_TIPS
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

    # Get the min/mid/max ground speed fits
    offset_distance_at_t = video_data.TIME_VIDEO_END_ASPHALT.time
    gs_fits = [plot_common.get_gs_fit(err) for err in video_data.ErrorDirection]
    offsets = [
        video_data.RUNWAY_LEN_M - video_analysis.ground_speed_integral(0, offset_distance_at_t, gs_fit)
        for gs_fit in gs_fits
    ]
    # Establish observer
    observer_xy_start_runway = plot_common.observer_xy()

    notes = [
        '"{}"'.format('Aspects, errors, and polynomial fit.'),
        'Columns:',
        '1: time (s)',
        '2: horizontal_angle (deg)',
        '3: -dt',
        '4: +dt',
        '5: -dy (deg)',
        '6: +dy (deg)',
        '7: horizontal_angle_fit (deg)',
        '8: vertical_angle (deg)',
        '9: -dt',
        '10: +dt',
        '11: -dy (deg)',
        '12: +dy (deg)',
        '13: vertical_angle_fit (deg)',
    ]
    if len(notes):
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))
    plot_common.gnuplot_write_arrays(
        stream,
        aspect_from_wing_tips_with_errors,
        aspect_fitted_from_wing_tips,
    )
    return []


def gnuplot_angle_of_view_plt() -> str:
    return """# set logscale x
set grid
set title "Angle of View."
set xlabel "Video Time (s)"
set mxtics 5
#set xrange [0:3000]
#set xtics
#set format x ""

# set logscale y
set ylabel "Angle (degrees)"
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

plot "{file_name}.dat" using 1:2:3:4:5:6 title "Horizontal View" lt 1 w xyerrorbars, \\
    "{file_name}.dat" using 1:7 title "Horizontal View fit" lw 2 lt 1 w lines smooth bezier, \\
    "{file_name}.dat" using 1:8:9:10:11:12 title "Vertical View" lt 2 w boxxyerror, \\
    "{file_name}.dat" using 1:13 title "Vertical View fit" lw 2 lt 2 w lines smooth bezier

reset
"""