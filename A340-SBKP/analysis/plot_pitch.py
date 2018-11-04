import sys
import typing

import numpy as np

from analysis import pitch
from analysis import video_data
from analysis import plot_common


def gnuplot_pitch(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    arrays = {
        min_max: pitch.pitches(min_max) for min_max in list(video_data.ErrorDirection)
    }
    timebase = arrays[video_data.ErrorDirection.MID][:, 0]
    aspect_with_errors = np.column_stack(
        (
            timebase,
            arrays[video_data.ErrorDirection.MID][:, 1],
            arrays[video_data.ErrorDirection.MIN][:, 0],
            arrays[video_data.ErrorDirection.MAX][:, 0],
            arrays[video_data.ErrorDirection.MIN][:, 1],
            arrays[video_data.ErrorDirection.MAX][:, 1],
        )
    )
    aspect_fitted = pitch.pitch_fitted_line()
    result = [
        '# "{}"'.format('Pitch (degrees), errors, and polynomial fit.'),
        '# "{}"'.format('t, -dt, +dt, -dy, +dy, fit.'),
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

    plot_common.gnuplot_write_arrays(
        stream,
        aspect_with_errors,
        aspect_fitted,
    )
    return []


def gnuplot_pitch_plt() -> str:
    return """# set logscale x
set grid
set title "Pitch Angle."
set xlabel "Video Time (s)"
#set xrange [0:3000]
#set xtics
#set format x ""

# set logscale y
set ylabel "Pitch (degrees)"
#set yrange [100:-1000]
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

set key off

set output "{file_name}.svg"   # choose the output device

set arrow from 18,-1.5 to 23,5.7 lw 3.5 lc rgb "blue"
set label 1 "1.4 °/s" at 21.5,2.5 font ",14"

set arrow from 29,6.7 to 31,9.5 lw 3.5 lc rgb "blue"
set label 2 "1.4 °/s" at 30.5,7.5 font ",14"

# Nose wheel off at around 00:17:27 i.e. 17.9s
set arrow from 17.9,6 to 17.9,0 lw 2 lc rgb "black"
set label 3 "Nose wheel off" at 17.9,6.5 font ",12" center

# Main gear off at around 00:25:19 i.e. 25.63
set arrow from 25.6,10.5 to 25.6,8 lw 2 lc rgb "black"
set label 4 "Main wheels off" at 25.6,11 font ",12" center

# Smoothing the line does not seem to be meaningful
plot "{file_name}.dat" using 1:2:3:4:5:6 title "Raw data" w xyerrorbars lw 1.5#, \\
    "{file_name}.dat" using 1:2 with lines smooth csplines

reset
"""