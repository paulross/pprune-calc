import sys
import typing

from analysis import plot_constants
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils


def gnuplot_ground_transits(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    result = [
        '# "{}"'.format('Distance of aircraft down the runway when passing ground transit lines.')
    ]
    notes = [
        'time x(m) y(m) x(y=0)(m) y==0(m) Name'
    ]
    if len(notes):
        stream.write('#\n')
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))

    gs_fit = video_analysis.ground_speed_curve_fit(video_data.ErrorDirection.MID)
    time_dist_brng = video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, video_data.ErrorDirection.MID)
    ((observer_x_mean, observer_x_std), (observer_y_mean, observer_y_std)) = video_analysis.observer_position_mean_std(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )

    observer_xy_start_runway = observer_x_mean + 1182, observer_y_mean
    # Google earth
    observer_xy_start_runway = (3457.9, -655.5)
    computed_data = []
    # Y range 2000m is 800px so a 50m wide runway would be 800 * 50 / 2000 = 20px
    computed_data.append(
        'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw 20 lc rgb "#C0C0C0"'.format(
            x0=0.0,
            y0=0.0,
            x1=3240,
            y1=0,
        )
    )
    for t, k in video_data.GOOGLE_EARTH_EVENTS:
        lat, lon = video_data.GOOGLE_EARTH_POSITIONS_LAT_LONG[k]
        event_time = video_data.GOOGLE_EARTH_EVENT_MAP[k]
        x, y = video_utils.lat_long_to_xy(
            video_data.GOOGLE_EARTH_DATUM_LAT_LONG[0],
            video_data.GOOGLE_EARTH_DATUM_LAT_LONG[1],
            video_data.GOOGLE_EARTH_X_AXIS,
            lat,
            lon,
        )
        x_intercept = video_utils.transit_x_axis_intercept(x, y, *observer_xy_start_runway)
        stream.write(
            '{t:<6.1f} {x:6.1f} {y:6.1f} {x_runway:6.1f} 0.0 # {label:}\n'.format(
                t=event_time, x=x, y=y, x_runway=x_intercept, label=k
            )
        )
        y_arrow_start = y if y > 0 else 0.0
        x_arrow_start = x if y > 0 else x_intercept
        computed_data.append(
            'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} lt -1 lw 0.75 nohead'.format(
                x0=x_arrow_start,
                y0=y_arrow_start,
                x1=observer_xy_start_runway[0],
                y1=observer_xy_start_runway[1],
            )
        )
    return computed_data


def gnuplot_ground_transits_plt() -> str:
    return """# set logscale x
set grid
set title "Transits to Observer"
set xlabel "Distance from start of runway (m)"
#set xtics 2100,100,2400
set xtics 500
#set xtics autofreq
set xrange [0:3700]
#set format x ""

# set logscale y
set ylabel "Distance from runway centerline (+ve right, -ve left)"
set yrange [-1100:1100] reverse
#set yrange [:10]
#set yrange [-600:-900] reverse
set ytics 200
#set ytics autofreq
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 2
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set key off

set terminal svg size 800,600

{computed_data}

set output "{file_name}.svg"

plot "{file_name}.dat" using 2:3 title "Transit points" ps 1.5, \\
    "{file_name}.dat" using 4:5 title "Runway intersection" ps 1.0
reset
"""