import itertools
import sys
import typing

from analysis import plot_constants, plot_common
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils
from analysis.video_data import GOOGLE_EARTH_FULL_TRANSITS, GOOGLE_EARTH_POSITIONS_LAT_LONG


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
    # time_dist_brng = video_analysis.observer_time_distance_bearing_from_wing_tips(gs_fit, video_data.ErrorDirection.MID)
    # ((obs_x_mean, obs_x_std), (obs_y_mean, obs_y_std)) = plot_common.observer_xy_with_std_from_aspects()
    ((obs_x_mean, obs_x_std), (obs_y_mean, obs_y_std)) = video_analysis.observer_position_mean_std_from_full_transits()
    # observer_xy_start_runway = plot_common.observer_xy()
    computed_data = []
    # Draw runway
    # Y range 2000m is 800px so a 50m wide runway would be 800 * 50 / 2000 = 20px
    computed_data.append(
        'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw 20 lc rgb "#C0C0C0" back'.format(
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
        x_intercept = video_utils.transit_x_axis_intercept(x, y, obs_x_mean, obs_y_mean)
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
                x1=obs_x_mean,
                y1=obs_y_mean,
                colour=colour,
            )
        )
        rotate = 90 if x < 500 else 00
        x_offset = 0 if x < 500 else -35
        y_offset = 35 if x < 500 else 0
        computed_data.append(
            'set label "{label:}" at {x:.1f},{y:.1f} right font ",8" rotate by {rotate}'.format(
                label=k,
                x=x+x_offset,
                y=y+y_offset,
                rotate=rotate,
            )
        )
    # Label observer
    computed_data.append(
        'set label "Observer X={x_mean:.0f} ±{x_err:.0f}m Y={y_mean:.0f} ±{y_err:.0f} m" at {x:.0f},{y:.0f} right font ",12"'.format(
            x_mean=obs_x_mean,
            x_err=obs_x_std,#(x_max - x_min) / 2,
            y_mean=obs_y_mean,
            y_err=obs_y_std,#(y_max - y_min) / 2,
            x=obs_x_mean-1000,
            y=obs_y_mean,
        )
    )
    computed_data.append(
        'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lt -1 lw 2 empty'.format(
            obs_x_mean-1000,
            obs_y_mean,
            obs_x_mean-25,
            obs_y_mean,
        )
    )
    return computed_data


def gnuplot_ground_transits_plt() -> str:
    return """# set logscale x
set colorsequence classic
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
set yrange [1100:-1100] reverse
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
        'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw 20 lc rgb "#C0C0C0" back'.format(
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
        computed_data.append(
            'set label "t={t:.1f}s x={x_runway:.0f}m" at {x:.0f},{y:.0f} right font ",9" textcolor rgb "#007F00" rotate by -30 front'.format(
                t=transit_line.time.time,
                x_runway=x_intercept,
                x=x_intercept-20,
                y=0+-20,
            )
        )
    computed_data.extend(plot_common.full_transit_labels_and_arrows('#0000FF', 0.75))
    # # Apply positional error and plot
    # # 808080
    # computed_data.extend(
    #     plot_common.full_transit_arrows_with_position_error(
    #         '#FF0000', video_data.GOOGLE_EARTH_ERROR, 0.5
    #     )
    # )
    # computed_data.extend(
    #     plot_common.full_transit_arrows_with_position_error(
    #         '#0000FF', -video_data.GOOGLE_EARTH_ERROR, 0.5
    #     )
    # )
    # Label and arrow to observers position
    observer_x_mean, observer_x_diff, observer_y_mean, observer_y_diff = plot_common.observer_position_from_full_transits()
    computed_data.extend(
        [
            'set label "X={x_mean:.0f} ±{x_err:.0f}m Y={y_mean:.0f} ±{y_err:.0f} m" at {x:.0f},{y:.0f} right font ",12"'.format(
                x_mean=observer_x_mean,
                x_err=observer_x_diff,
                y_mean=observer_y_mean,
                y_err=observer_y_diff,
                x=observer_x_mean-510,
                y=observer_y_mean-110,
            ),
            'set arrow from {:.0f},{:.0f} to {:.0f},{:.0f} lt -1 lw 2 empty'.format(
                observer_x_mean - 500, observer_y_mean-100, observer_x_mean, observer_y_mean,
            ),
        ]
    )
    return computed_data


def markdown_table_distance_from_start_by_transit() -> typing.Tuple[typing.List[str], str]:
    result = [
        '| Video Time (mm:ss:ff) | Distance from Start of Runway (m) |',
        '| --- | ---: |',
    ]

    observer_xy_start_runway = video_utils.XY(*plot_common.observer_xy())
    for transit_line in video_data.GOOGLE_EARTH_FULL_TRANSITS:
        x_intercept = video_utils.transit_x_axis_intercept(
            transit_line.frm.xy.x,
            transit_line.frm.xy.y,
            *observer_xy_start_runway
        )
        result.append(
            '| {:02d}:{:02d}:{:02d} | {x_runway:.0f} |'.format(
                transit_line.time.min, transit_line.time.sec, transit_line.time.frame,
                x_runway=x_intercept,
            )
        )
    return result, 'Aircraft Position from Runway Start from Full Transits'


def gnuplot_full_transits_plt() -> str:
    return """# set logscale x
set colorsequence classic
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
# set yrange [-1400:1100] reverse
set yrange [1100:-1400]
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

set terminal svg size 1200,600

{computed_data}

set output "{file_name}.svg"

plot "{file_name}.dat" using 2:3 title "Transit points" ps 1.5, \\
    "{file_name}.dat" using 4:5 title "Runway intersection" ps 1.0
reset
"""


def markdown_table_full_transits() -> typing.Tuple[typing.List[str], str]:
    ret = [
        '| Video Time (mm:ss:ff) | First Point | First Point Lat, Long | First Point X, Y (m) | Second Point | Second Point Lat, Long | Second Point X, Y (m) |',
        '| ---: | --- | ---: | ---: | --- | ---: | ---: |',
    ]
    for transit in GOOGLE_EARTH_FULL_TRANSITS:
        lat_long_frm = GOOGLE_EARTH_POSITIONS_LAT_LONG[transit.frm.label]
        lat_long_to = GOOGLE_EARTH_POSITIONS_LAT_LONG[transit.to.label]
        ret.append(
            '| {:02d}:{:02d}:{:02d} | {} | {:.6f}, {:.6f} | {:.0f}, {:.0f} | {} | {:.6f}, {:.6f} | {:.0f}, {:.0f} |'.format(
                transit.time.min, transit.time.sec, transit.time.frame,
                transit.frm.label, lat_long_frm.lat, lat_long_frm.long, transit.frm.xy.x, transit.frm.xy.y,
                transit.to.label, lat_long_to.lat, lat_long_to.long, transit.to.xy.x, transit.to.xy.y,
        ))
    return ret, 'Full transits to Observer from Google Earth Positions'

def print_full_transits():
    for transit in GOOGLE_EARTH_FULL_TRANSITS:
        print(
            'Full transit at {} from {:8.3f} {:8.3f} "{}"->"{}"'.format(
                transit.time,
                transit.frm.xy, transit.to.xy,
                transit.frm.label, transit.to.label,
            )
        )
    print()
    print('\n'.join(markdown_table_full_transits()))
    print()
    crossing_x = []
    crossing_y = []
    for num, (i, j) in enumerate(itertools.combinations(range(len(GOOGLE_EARTH_FULL_TRANSITS)), 2)):
        transit1: video_data.FullTransitLine = GOOGLE_EARTH_FULL_TRANSITS[i]
        transit2: video_data.FullTransitLine = GOOGLE_EARTH_FULL_TRANSITS[j]
        crossing = video_utils.intersect_two_lines(
            transit1.frm.xy, transit1.to.xy, transit2.frm.xy, transit2.to.xy,
        )
        crossing_x.append(crossing.x)
        crossing_y.append(crossing.y)
        print(
            '[{:2d}] Full transit crossing {:8.3f} "{}"->"{}" and  "{}"->"{}"'.format(
                num,
                crossing,
                transit1.frm.label, transit1.to.label,
                transit2.frm.label, transit2.to.label,
            )
        )
    print(
        'X: min={:8.3f} mean={:8.3f} max={:8.3f} range={:8.3f}'.format(
            min(crossing_x), sum(crossing_x) / len(crossing_x), max(crossing_x), max(crossing_x) - min(crossing_x),
        )
    )
    print(
        'Y: min={:8.3f} mean={:8.3f} max={:8.3f} range={:8.3f}'.format(
            min(crossing_y), sum(crossing_y) / len(crossing_y), max(crossing_y), max(crossing_y) - min(crossing_y),
        )
    )


if __name__ == '__main__':
    print_full_transits()