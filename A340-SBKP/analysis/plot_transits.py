import sys
import typing

from analysis import plot_constants, plot_common
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
    ((observer_x_mean, observer_x_std), (observer_y_mean, observer_y_std)) = plot_common.observer_xy_with_std()
    observer_xy_start_runway = plot_common.observer_xy()
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
        event_time = video_data.GOOGLE_EARTH_EVENT_MAP[k]
        x, y = video_utils.lat_long_to_xy(
            video_data.GOOGLE_EARTH_DATUM_LAT_LONG,
            video_data.GOOGLE_EARTH_X_AXIS,
            video_data.GOOGLE_EARTH_POSITIONS_LAT_LONG[k],
        )
        x_intercept = video_utils.transit_x_axis_intercept(x, y, *observer_xy_start_runway)
        stream.write(
            '{t:<6.1f} {x:6.1f} {y:6.1f} {x_runway:6.1f} 0.0 # {label:}\n'.format(
                t=event_time, x=x, y=y, x_runway=x_intercept, label=k
            )
        )
        y_arrow_start = y if y > 0 else 0.0
        x_arrow_start = x if y > 0 else x_intercept
        colour = 'lc rgb "#0000FF"' if video_data.transit_is_simultaneous(k) else 'lt -1'
        computed_data.append(
            'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} {colour:s} lw 0.75 nohead'.format(
                x0=x_arrow_start,
                y0=y_arrow_start,
                x1=observer_xy_start_runway[0],
                y1=observer_xy_start_runway[1],
                colour=colour,
            )
        )
        computed_data.append(
            'set label "{label:}" at {x:.1f},{y:.1f} right font ",8" rotate by 60'.format(
                label=k,
                x=x_arrow_start-25,
                y=y_arrow_start+25,
            )
        )
    # Label observer
    computed_data.append(
        'set label "Observer X={x_mean:.0f} ±{x_err:.0f}m Y={y_mean:.0f} ±{y_err:.0f} m" at {x:.0f},{y:.0f} right font ",12"'.format(
            x_mean=observer_x_mean,
            x_err=observer_x_std,#(x_max - x_min) / 2,
            y_mean=observer_y_mean,
            y_err=observer_y_std,#(y_max - y_min) / 2,
            x=observer_x_mean-1000+plot_common.x_offset(),
            y=observer_y_mean,
        )
    )
    computed_data.append(
        'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lt -1 lw 2 empty'.format(
            observer_x_mean-1000+plot_common.x_offset(),
            observer_y_mean,
            observer_x_mean+plot_common.x_offset()-25,
            observer_y_mean,
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
# set xrange [2250:3700]
#set format x ""

# set logscale y
set ylabel "Distance from runway centerline (+ve right, -ve left)"
set yrange [-1100:1100] reverse
# set yrange [400:-800] reverse
#set yrange [:10]
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

def gnuplot_full_transits(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    result = [
        '# "{}"'.format('Full transit lines.')
    ]
    notes = [
        'time x(m) y(m) x(y=0)(m) y==0(m) Name'
    ]
    if len(notes):
        stream.write('#\n')
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))

    observer_xy_start_runway = video_utils.XY(*plot_common.observer_xy())
    # Y range 2000m is 800px so a 50m wide runway would be 800 * 50 / 2000 = 20px
    computed_data = [
        'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw 20 lc rgb "#C0C0C0"'.format(
            x0=0.0,
            y0=0.0,
            x1=3240,
            y1=0,
        )
    ]
    for transit_line in video_data.GOOGLE_EARTH_FULL_TRANSITS:
        x_intercept = video_utils.transit_x_axis_intercept(
            transit_line.frm.xy.x,
            transit_line.frm.xy.y,
            *observer_xy_start_runway
        )
        stream.write(
            '{t:<6.1f} {x:6.1f} {y:6.1f} {x_runway:6.1f} 0.0 # {label:}\n'.format(
                t=transit_line.time.time,
                x=transit_line.frm.xy.x,
                y=transit_line.frm.xy.y,
                x_runway=x_intercept,
                label='{}->{}'.format(transit_line.frm.label, transit_line.to.label)
            )
        )
        stream.write(
            '{t:<6.1f} {x:6.1f} {y:6.1f} {x_runway:6.1f} 0.0 # {label:}\n'.format(
                t=transit_line.time.time,
                x=transit_line.to.xy.x,
                y=transit_line.to.xy.y,
                x_runway=x_intercept,
                label='{}->{}'.format(transit_line.frm.label, transit_line.to.label)
            )
        )
    computed_data.extend(plot_common.full_transit_labels_and_arrows())
    return computed_data
    # gs_fit = video_analysis.ground_speed_curve_fit(video_data.ErrorDirection.MID)
    # time_dist_brng = video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, video_data.ErrorDirection.MID)
    # ((observer_x_mean, observer_x_std), (observer_y_mean, observer_y_std)) = plot_common.observer_xy_with_std()
    # observer_xy_start_runway = plot_common.observer_xy()
    # computed_data = []
    # # Y range 2000m is 800px so a 50m wide runway would be 800 * 50 / 2000 = 20px
    # computed_data.append(
    #     'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw 20 lc rgb "#C0C0C0"'.format(
    #         x0=0.0,
    #         y0=0.0,
    #         x1=3240,
    #         y1=0,
    #     )
    # )
    # for t, k in video_data.GOOGLE_EARTH_EVENTS:
    #     event_time = video_data.GOOGLE_EARTH_EVENT_MAP[k]
    #     x, y = video_utils.lat_long_to_xy(
    #         video_data.GOOGLE_EARTH_DATUM_LAT_LONG,
    #         video_data.GOOGLE_EARTH_X_AXIS,
    #         video_data.GOOGLE_EARTH_POSITIONS_LAT_LONG[k],
    #     )
    #     x_intercept = video_utils.transit_x_axis_intercept(x, y, *observer_xy_start_runway)
    #     stream.write(
    #         '{t:<6.1f} {x:6.1f} {y:6.1f} {x_runway:6.1f} 0.0 # {label:}\n'.format(
    #             t=event_time, x=x, y=y, x_runway=x_intercept, label=k
    #         )
    #     )
    #     y_arrow_start = y if y > 0 else 0.0
    #     x_arrow_start = x if y > 0 else x_intercept
    #     colour = 'lc rgb "#0000FF"' if video_data.transit_is_simultaneous(k) else 'lt -1'
    #     computed_data.append(
    #         'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} {colour:s} lw 0.75 nohead'.format(
    #             x0=x_arrow_start,
    #             y0=y_arrow_start,
    #             x1=observer_xy_start_runway[0],
    #             y1=observer_xy_start_runway[1],
    #             colour=colour,
    #         )
    #     )
    #     computed_data.append(
    #         'set label "{label:}" at {x:.1f},{y:.1f} right font ",8" rotate by 60'.format(
    #             label=k,
    #             x=x_arrow_start-25,
    #             y=y_arrow_start+25,
    #         )
    #     )
    # # Label observer
    # computed_data.append(
    #     'set label "Observer X={x_mean:.0f} ±{x_err:.0f}m Y={y_mean:.0f} ±{y_err:.0f} m" at {x:.0f},{y:.0f} right font ",12"'.format(
    #         x_mean=observer_x_mean,
    #         x_err=observer_x_std,#(x_max - x_min) / 2,
    #         y_mean=observer_y_mean,
    #         y_err=observer_y_std,#(y_max - y_min) / 2,
    #         x=observer_x_mean-1000+plot_common.x_offset(),
    #         y=observer_y_mean,
    #     )
    # )
    # computed_data.append(
    #     'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lt -1 lw 2 empty'.format(
    #         observer_x_mean-1000+plot_common.x_offset(),
    #         observer_y_mean,
    #         observer_x_mean+plot_common.x_offset()-25,
    #         observer_y_mean,
    #     )
    # )
    # return computed_data


def gnuplot_full_transits_plt() -> str:
    return """# set logscale x
set grid
set title "Full Transits to Observer"
set xlabel "Distance from start of runway (m)"
#set xtics 2100,100,2400
set xtics 500
#set xtics autofreq
set xrange [0:3700]
# set xrange [2250:3700]
#set format x ""

# set logscale y
set ylabel "Distance from runway centerline (+ve right, -ve left)"
set yrange [-1400:1100] reverse
# set yrange [400:-800] reverse
#set yrange [:10]
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

plot "{file_name}.dat" using 2:3 title "Transit points" ps 1.0, \\
    "{file_name}.dat" using 4:5 title "Runway intersection" ps 1.0
reset
"""
