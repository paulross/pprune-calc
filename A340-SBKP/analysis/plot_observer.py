import math
import pprint
import sys
import typing

import numpy as np

from analysis import plot_common
from analysis import plot_constants
from analysis import video_analysis
from analysis import video_data


def gnuplot_observer_time_distance_bearing(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    result = [
        '# "{}"'.format('')
    ]
    notes = [
        't(s) x_0(m) y_0(m) bearing(deg) x_1(m) y_1(m)'
    ]
    notes = [
        '"{}"'.format('Video time, distance and bearing (s, m, degrees).'),
        'Mostly this is information only as only the x value in column 2 is used to plot',
        'along the y=0 axis',
        'Columns:',
        '1: t (s)',
        '2: x_from (m)',
        '3: y_from (m)',
        '4: bearing (deg)',
        '5: x_to (m)',
        '6: y_to (m)',
    ]
    if len(notes):
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))

    FORMAT = '{:8.3f}'
    gs_fit = video_analysis.ground_speed_curve_fit(video_data.ErrorDirection.MID)
    # These are ndarrays of (time, distance, aspect, aspect_error)
    # time_dist_brng = video_analysis.observer_time_distance_bearing(gs_fit, video_data.ErrorDirection.MID)

    # time_dist_brng = video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, video_data.ErrorDirection.MID)

    # Get the errors in bearing. This produces three ndarrays of (time, distance, aspect, aspect_error)
    # where the time and distance are the same (and probably the aspect error) so we can combine them
    # to create an list of (time, distance, bearing_min, bearing_mid, bearing_max)
    time_dist_brng_s = [
        video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, err_direction)
        for err_direction in list(video_data.ErrorDirection)
    ]
    assert len(time_dist_brng_s) == 3
    assert len(set([len(v) for v in time_dist_brng_s])) == 1
    rows = len(time_dist_brng_s[0])
    time_distance_bearing_limits = []
    for r in range(rows):
        # Time should be the same
        assert time_dist_brng_s[0][r, 0] == time_dist_brng_s[1][r, 0]
        assert time_dist_brng_s[0][r, 0] == time_dist_brng_s[2][r, 0]
        # Distance should be the same
        assert time_dist_brng_s[0][r, 1] == time_dist_brng_s[1][r, 1]
        assert time_dist_brng_s[0][r, 1] == time_dist_brng_s[2][r, 1]
        time_distance_bearing_limits.append(
            (
                time_dist_brng_s[0][r, 0], # time
                time_dist_brng_s[0][r, 1], # distance
                time_dist_brng_s[0][r, 2], # bearing_min
                time_dist_brng_s[1][r, 2], # bearing_mid
                time_dist_brng_s[2][r, 2], # bearing_max
            )
        )
    # print('TRACE: time_distance_bearing_limits')
    # for row in time_distance_bearing_limits:
    #     print('{:6.1f} {:6.1f} {:8.3f} {:8.3f} {:8.3f}'.format(*row))
    y_value = -950
    y_0 = 0.0
    arrow_texts = []
    label_texts = []
    for i in range(len(time_dist_brng_s[1])):
        t = time_dist_brng_s[1][i, 0]
        x_0 = time_dist_brng_s[1][i, 1]
        bearing = time_dist_brng_s[1][i, 2]
        if abs(math.sin(math.radians(bearing))) < 0.01:
            radius = abs(y_value - y_0)
        else:
            radius = abs(y_value / math.sin(math.radians(bearing)))
        x_1 = x_0 + radius * math.cos(math.radians(bearing))
        y_1 = y_0 + radius * math.sin(math.radians(bearing))
        part_line = ['{:.1f}'.format(t),]
        part_line.extend([FORMAT.format(v) for v in (x_0, y_0, bearing, x_1, y_1)])
        result.append(' '.join(part_line))
        if t < video_data.TIME_VIDEO_NOSEWHEEL_OFF.time:
            line_style = 7
        elif t >= video_data.TIME_VIDEO_MAINWHEEL_OFF.time:
            line_style = 14
        else:
            line_style = 6
        # Arrow line styles, SVG terminal.
        # 0 Dotted grey
        # 1 thin blue
        # 2 green
        # 3 blue
        # 4 cyan
        # 5 Dark green
        # 6 Dark blue
        # 14 Red
        arrow_texts.append(
            'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} ls {ls:d} nohead'.format(
                x_0, y_0, x_1, y_1,
                ls=4 if i < plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS else line_style
                # ls=i
            )
        )
        label_texts.append(
            # Gnuplot label numbering starts from 1
            'set label {} "t={:.1f}" at {:.0f},20 right rotate by 60 font ",9"'.format(
                i + 1, time_dist_brng_s[1][i, 0], x_0# - 25
            )
        )
    # print('# Arrows:')
    # print('\n'.join(arrow_texts))
    # print('# Labels:')
    # print('\n'.join(label_texts))
    stream.write('\n'.join(result))

    # Add annotation to identify observer
    ((x_mean, x_std), (y_mean, y_std)) = video_analysis.observer_position_mean_std(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )
    label_texts.append(
        'set label "Mean position at x={x:.0f}, y={y:.0f}" at {x_pos:.0f},{y_pos:.0f} right font ",14"'.format(
            x=x_mean,
            y=y_mean,
            x_pos=x_mean - 500,
            y_pos=y_mean,
        )
    )
    arrow_texts.append(
        'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lw 3'.format(
            x_mean - 500 + 25,
            y_mean,
            x_mean,
            y_mean,
        )
    )

    return arrow_texts + label_texts


def gnuplot_observer_time_distance_bearing_with_yaw(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    result = [
        '# "{}"'.format('Video time, distance and bearing (s, m, degrees).')
    ]
    notes = [
        't(s) x_0(m) y_0(m) bearing(deg) x_1(m) y_1(m)'
    ]
    if len(notes):
        stream.write('#\n')
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))
    FORMAT = '{:8.3f}'
    gs_fit = video_analysis.ground_speed_curve_fit(video_data.ErrorDirection.MID)
    # time_dist_brng = video_analysis.observer_time_distance_bearing(gs_fit, video_data.ErrorDirection.MID)
    time_dist_brng = video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, video_data.ErrorDirection.MID)
    # time_dist_brng = video_analysis.time_distance_bearing_from_fits(time_interval=1.0)
    ((x_mean, x_std), (y_mean, y_std)) = video_analysis.observer_position_mean_std(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )
    print('Observer at:', ((x_mean, x_std), (y_mean, y_std)))

    y_value = -950
    y_0 = 0.0
    arrow_texts = []
    label_texts = []
    for i in range(len(time_dist_brng)):
        t = time_dist_brng[i, 0]
        x_0 = time_dist_brng[i, 1]
        bearing = time_dist_brng[i, 2]
        computed_bearing = math.degrees(math.atan2(y_mean, x_mean - x_0))
        computed_bearing %= 360
        distance = math.sqrt(y_mean**2 + (x_mean - x_0)**2)
        # Allow for assumed yaw of the aircraft from video_date.YAW_PROFILE
        # yaw = video_utils.interpolate(video_data.YAW_PROFILE[:, 0], video_data.YAW_PROFILE[:, 1], t)
        yaw = computed_bearing - bearing
        y_err = math.sin(math.radians(yaw)) * distance
        # print('TRACE: t={:6.1f} x_0={:6.1f} bearing={:6.1f} computed_bearing={:6.1f} yaw={:6.1f} y_err={:6.1f}'.format(
        #     t, x_0, bearing, computed_bearing, yaw, y_err
        # ))
        bearing += yaw
        if abs(math.sin(math.radians(bearing))) < 0.01:
            radius = abs(y_value - y_0)
        else:
            radius = abs(y_value / math.sin(math.radians(bearing)))
        x_1 = x_0 + radius * math.cos(math.radians(bearing))
        y_1 = y_0 + radius * math.sin(math.radians(bearing))
        part_line = ['{:.1f}'.format(t),]
        part_line.extend([FORMAT.format(v) for v in (x_0, y_0, bearing, x_1, y_1)])
        result.append(' '.join(part_line))
        if t < video_data.TIME_VIDEO_NOSEWHEEL_OFF.time:
            line_style = 7
        elif t >= video_data.TIME_VIDEO_MAINWHEEL_OFF.time:
            line_style = 14
        else:
            line_style = 6
        # Arrow line styles, SVG terminal.
        # 0 Dotted grey
        # 1 thin blue
        # 2 green
        # 3 blue
        # 4 cyan
        # 5 Dark green
        # 6 Dark blue
        # 14 Red
        arrow_texts.append(
            'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} ls {ls:d} nohead'.format(
                x_0, y_0, x_1, y_1,
                ls=4 if i < plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS else line_style
                # ls=i
            )
        )
        label_texts.append(
            # Gnuplot label numbering starts from 1
            'set label {} "t={:.1f}" at {:.0f},20 right rotate by 60 font ",9"'.format(
                i + 1, time_dist_brng[i, 0], x_0# - 25
            )
        )
    # observer_error = math.sqrt(x_std**2 + y_std**2)
    # Add annotation to identify observer
    label_texts.append(
        'set label "Observer assumed at x={x:.0f}, y={y:.0f}" at {x_pos:.0f},{y_pos:.0f} right font ",14"'.format(
            x=x_mean,
            y=y_mean,
            x_pos=x_mean - 500,
            y_pos=y_mean,
        )
    )
    arrow_texts.append(
        'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lw 3'.format(
            x_mean - 500 + 25,
            y_mean,
            x_mean,
            y_mean,
        )
    )
    # print('# Arrows:')
    # print('\n'.join(arrow_texts))
    # print('# Labels:')
    # print('\n'.join(label_texts))
    stream.write('\n'.join(result))
    return arrow_texts + label_texts


def gnuplot_observer_time_distance_bearing_plt() -> str:
    return """# set logscale x
set grid
set title "Bearings to Observer\\n(NOTE: Axes not to common scale)"
set xlabel "Distance from t=0 (m)"
set xrange [0:3000]
#set xrange [2200:2300]
set xtics
#set format x ""

# set logscale y
set ylabel "Offset to Observer (m)"
set yrange [200:-1000]
#set yrange [-750:-800]
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

set key off

set output "{file_name}.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

y_base_value = 0

#set style line 1 lt 1 lw 2

set style line 1 lc rgb "blue" lw 0.5

#set style arrow 1 nohead ls 1

{computed_data}

plot "{file_name}.dat" using 2:(y_base_value)
reset
"""


def gnuplot_observer_xy(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    notes = [
        '"{}"'.format('Estimated x/y of observer.'),
        'Columns:',
        '1: x (m)',
        '2: y minumum (m)',
        '3: y mid (m)',
        '4: y maximum (m)',
    ]
    if len(notes):
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))
    # observer_xy array
    observations = [
        video_analysis.observer_position_combinations(
            min_mid_max=error_direction,
            baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
            ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
            t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
        )[0] for error_direction in list(video_data.ErrorDirection)
    ]
    plot_common.gnuplot_write_arrays(stream, *observations)
    # Print header twice, once for x, once for y.
    for i in range(2):
        axis_name = 'X' if i == 0 else 'Y'
        print('{}: {:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}  '.format(
            axis_name, 'Count', 'Min', 'Median', 'Mean', 'Max', 'Std', 'Range'), end=''
        )
    print()
    for obs in observations:
        for i in range(2):
            axis_name = 'X' if i == 0 else 'Y'
            print('{}: {:8d} {:8.0f} {:8.0f} {:8.0f} {:8.0f} {:8.0f} {:8.0f}  '.format(
                axis_name, len(obs),
                np.min(obs, axis=0)[i], np.median(obs, axis=0)[i],
                np.mean(obs, axis=0)[i], np.max(obs, axis=0)[i],
                np.std(obs, axis=0)[i], np.max(obs, axis=0)[i] - np.min(obs, axis=0)[i],
            ), end='')
        print()
    # x_mean = np.mean(observations[1], axis=0)[0]
    # x_min = np.min(observations[1], axis=0)[0]
    # x_max = np.max(observations[1], axis=0)[0]
    # x_std = np.std(observations[1], axis=0)[0]
    # y_mean = np.mean(observations[1], axis=0)[1]
    # y_min = np.min(observations[1], axis=0)[1]
    # y_max = np.max(observations[1], axis=0)[1]
    # y_std = np.std(observations[1], axis=0)[1]
    ((x_mean, x_std), (y_mean, y_std)) = video_analysis.observer_position_mean_std(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )
    return [
        'set title "Observers Position [{:d} observations]"'.format(len(observations[1])),
        'set label "X={x_mean:.0f} ±{x_err:.0f}m Y={y_mean:.0f} ±{y_err:.0f} m" at {x:.0f},{y:.0f} center font ",14"'.format(
            x_mean=x_mean,
            x_err=x_std,#(x_max - x_min) / 2,
            y_mean=y_mean,
            y_err=y_std,#(y_max - y_min) / 2,
            x=x_mean-50,
            y=y_mean+45,
        ),
        'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lt -1 lw 2 empty'.format(
            x_mean-40, y_mean+45-8, x_mean, y_mean,
        ),
    ]


def gnuplot_observer_xy_plt() -> str:
    return """# set logscale x
set grid
set xlabel "X (m)"
#set xtics 2100,100,2400
# set xtics 100
set xtics autofreq
set mxtics 2
set xrange [2150:2350]
#set format x ""

# set logscale y
set ylabel "Y (m)"
# set yrange [] reverse
set yrange [-650:-850] reverse
# set ytics 100
set ytics autofreq
set mytics 2
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 2
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set key off

set terminal svg size 600,600

{computed_data}

set output "{file_name}.svg"

plot "{file_name}.dat" using 1:2 title "With -ve error" w points ps 0.5, \\
    "{file_name}.dat" using 1:3 title "No error" w points ps 0.5, \\
    "{file_name}.dat" using 1:4 title "With +ve error" w points ps 0.5
#plot "{file_name}.dat" using 1:3 title "Mid data" w points lt 6 ps 1
reset
"""