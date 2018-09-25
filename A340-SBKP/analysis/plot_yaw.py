import math
import sys
import typing

import numpy as np

from analysis import plot_common
from analysis import plot_constants
from analysis import video_analysis
from analysis import video_data


def gnuplot_aircraft_yaw(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    result = [
        '# "{}"'.format('Estimated yaw of aircraft.')
    ]
    notes = [
        'time yaw(degrees)'
    ]
    if len(notes):
        stream.write('#\n')
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))
    gs_fit = video_analysis.ground_speed_curve_fit(video_data.ErrorDirection.MID)
    # time_dist_brng = video_analysis.observer_time_distance_bearing(gs_fit, video_data.ErrorDirection.MID)
    time_dist_brng = video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, video_data.ErrorDirection.MID)
    # time_dist_brng = video_analysis.time_distance_bearing_from_fits(time_interval=1.0)

    # time_dist_brng is a four column array of (time, x_distance, aspect, aspect_error)
    # from the observed aspect data.
    # Units are (seconds, metres, degrees).

    time_yaw = []
    ((x_mean, x_std), (y_mean, y_std)) = video_analysis.observer_position_mean_std(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )
    observer_error = math.sqrt(x_std**2 + y_std**2)
    for t, x_distance, aspect, aspect_error in time_dist_brng:
        # Calculate the bearing from the observers assumed position to the aircraft position
        x_obs_aircraft = x_mean - x_distance
        obs_brng = math.degrees(
            math.atan2(y_mean, x_obs_aircraft)
        )
        obs_brng %= 360
        yaw = (obs_brng - aspect) % 360
        if yaw > 180.0:
            yaw -= 360
        # Compute error as the angle:
        # 2.0 * atan(OBSERVER_ASSUMED_POSITION_ERROR / observer-to_aircraft_distance)
        obs_aircraft_distance = math.sqrt(y_mean**2 + x_obs_aircraft**2)
        error = 2.0 * math.degrees(math.atan(observer_error / obs_aircraft_distance))
        # TODO: Take the estimated error from AIRCRAFT_ASPECTS_FROM_WING_TIPS
        error += aspect_error
        time_yaw.append((t, yaw, yaw - error, yaw + error))
        # print('TRACE: t={:8.1f} yaw={:6.3f}),'.format(t, yaw))
    # print('TRACE: time_yaw:')
    # pprint.pprint(time_yaw)
    plot_common.gnuplot_write_arrays(stream, np.array(time_yaw))
    return ['']


def gnuplot_aircraft_yaw_plt() -> str:
    return """# set logscale x
set grid
set title "Aircraft Deviation from Runway Heading{computed_data}"
set xlabel "Video Time (s)"
#set xtics 2100,100,2400
set xtics autofreq
#set xrange [2000:2500]
#set format x ""

# set logscale y
set ylabel "Deviation (degrees, +ve right, -ve left)"
set yrange [:10]
#set yrange [-600:-900] reverse
#set ytics 100
set ytics autofreq
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

set output "{file_name}.svg"

plot "{file_name}.dat" using 1:2:3:4 title "Estimated" w yerrorbars ps 1.25, \\
    "{file_name}.dat" using 1:2 title "Fit of best estimate" w linespoints ps 1.25 smooth csplines#bezier
reset
"""