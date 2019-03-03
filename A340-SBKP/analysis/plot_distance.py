import sys
import typing

import numpy as np

from analysis import plot_common
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils
from analysis.plot_common import get_distances_min_mid_max


def gnuplot_distance(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    return _gnuplot_distance(0.0, False, stream)


def gnuplot_distance_runway_end(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    return _gnuplot_distance(video_data.TIME_VIDEO_END_ASPHALT.time, True, stream)


def _gnuplot_distance(offset_distance_at_t: float,
                      include_labels_t_0: bool,
                      stream: typing.TextIO=sys.stdout,
                      ) -> typing.List[str]:
    """
    If offset_distance_at_t is non-zero an offset will be applied that is the
    runway length - the distance at that offset time.
    """
    three_dist_arrays = get_distances_min_mid_max(offset_distance_at_t)
    plot_common.gnuplot_write_arrays(stream, *three_dist_arrays)
    plot_data = ['# Start distance arrows and labels']
    if offset_distance_at_t == 0.0:
        text_offset = 0
    else:
        text_offset = 1000
    plot_data.extend(
        [
            # set arrow from -30.137,0 to -30.137,-791.8 lt 1
            'set arrow from {t:.3f},{offset:d} to {t:.3f},{d:.3f} lt {lt:d}'.format(
                t=three_dist_arrays[i][0, 0],
                offset=text_offset + i * 200,
                d=three_dist_arrays[i][0, 1],
                lt=i+1,
            ) for i in range(len(three_dist_arrays))
        ]
    )
    plot_data.extend(
        [
            # set label 1 "Calculated start at -30s, -790m" at -30.137,100 left font ",10" # rotate by 45
            'set label "Calculated start at {t:.1f}s, {d:.0f}m" at {t:.1f},{offset:d} left font ",9"'.format(
                t=three_dist_arrays[i][0, 0],
                offset=text_offset + 100 + i * 200,
                d=three_dist_arrays[i][0, 1],
            ) for i in range(len(three_dist_arrays))
        ]
    )
    plot_data.append('# End labels at start of take off')
    if include_labels_t_0:
        plot_data.append('# Labels at t=0')
        for i in range(len(three_dist_arrays)):
            d = video_utils.interpolate(three_dist_arrays[i][:, 0], three_dist_arrays[i][:, 1], 0.0)
            plot_data.append(
                # set arrow from -30.137,0 to -30.137,-791.8 lt 1
                'set arrow from {t:.3f},{d:.1f} to 0.0,{d:.3f} lt {lt:d}'.format(
                    t=6.0,
                    d=d,
                    lt=i + 1,
                )
            )
            plot_data.append(
                # set label 1 "Calculated start at -30s, -790m" at -30.137,100 left font ",10" # rotate by 45
                'set label "t=0.0s, d={d:.0f}m" at {t:.1f},{d:.1f} left font ",9"'.format(
                    t=6.0,
                    d=d,
                )
            )
        plot_data.append('# End labels at t=0')
    if offset_distance_at_t == 0.0:
        d_to = 1850
    else:
        d_to = video_data.RUNWAY_LEN_M - 100
    d_from = d_to - 850
    plot_data.append(
        'set arrow from {t:.3f},{d_from:d} to {t:.3f},{d_to:d} lt -1'.format(
            d_from=d_from,
            d_to=d_to,
            t=video_data.TIME_VIDEO_END_ASPHALT.time,
        )
    )
    plot_data.append(
        # set label 7 "End asphalt 27.8s" at 27.8,900 center font ",10"
        'set label "End asphalt {t:.1f}s" at {t:.1f},{d:d} center font ",10"'.format(
            d=d_from - 100,
            t=video_data.TIME_VIDEO_END_ASPHALT.time,
        )
    )

    if offset_distance_at_t == 0.0:
        plot_data.extend(
            [
                # set arrow from 17.8,1919 to 27.8,1919 as 4 lt 1
                'set arrow from {t0:.3f},{distance:.3f} to {t1:.3f},{distance:.3f} lt {lt:d}'.format(
                    t0=video_data.TIME_VIDEO_END_ASPHALT.time - 10,
                    t1=video_data.TIME_VIDEO_END_ASPHALT.time,
                    distance=np.interp(
                        video_data.TIME_VIDEO_END_ASPHALT.time,
                        three_dist_arrays[i][:, 0],
                        three_dist_arrays[i][:, 1],
                    ),
                    lt=i+1,
                ) for i in range(len(three_dist_arrays))
            ]
        )
        plot_data.extend(
            [
                # set label 4 "1920m" at 17,1920 right font ",10" # rotate by 45
                'set label "{distance:.0f}m" at {t:.1f},{distance:.1f} right font ",10"'.format(
                    t=video_data.TIME_VIDEO_END_ASPHALT.time - 10 - 1,
                    distance=np.interp(
                        video_data.TIME_VIDEO_END_ASPHALT.time,
                        three_dist_arrays[i][:, 0],
                        three_dist_arrays[i][:, 1],
                    ),
                ) for i in range(len(three_dist_arrays))
            ]
        )
    else:
        plot_data.append(
            'set arrow from {t0:.3f},{distance:.3f} to {t1:.3f},{distance:.3f} lt {lt:d}'.format(
                t0=video_data.TIME_VIDEO_END_ASPHALT.time - 10,
                t1=video_data.TIME_VIDEO_END_ASPHALT.time,
                distance=video_data.RUNWAY_LEN_M,
                lt=2,
            )
        )
        plot_data.append(
            'set label "{distance:.0f}m" at {t:.1f},{distance:.1f} right font ",10"'.format(
                t=video_data.TIME_VIDEO_END_ASPHALT.time - 10 - 1,
                distance=video_data.RUNWAY_LEN_M,
            )
        )
    plot_data.append('# End video')
    # TODO: Constants here, they should be computed.
    if offset_distance_at_t == 0.0:
        d_to = 2350
    else:
        d_to = 3700
    d_from = d_to - 850
    plot_data.append(
        # set arrow from 33.7,1500 to 33.7,2350 as 11 lt -1
        'set arrow from {t:.3f},{d_from:d} to {t:.3f},{d_to:d} lt -1'.format(
            t=video_data.TIME_VIDEO_END.time,
            d_from=d_from,
            d_to=d_to,
        )
    )
    plot_data.append(
        # set label 11 "End video 33.7s" at 33.7,1400 center font ",10" # rotate by 45
        'set label "End video {t:.1f}s" at {t:.1f},{d:d} center font ",10"'.format(
            t=video_data.TIME_VIDEO_END.time,
            d=d_from - 100
        )
    )
    if offset_distance_at_t == 0.0:
        # Plot individual arrows and labels of end of video
        plot_data.extend(
            [
                # set arrow from 23.7,2432.8 to 33.7,2432.8 as 8 lt 1
                'set arrow from {t0:.3f},{distance:.3f} to {t1:.3f},{distance:.3f} lt {lt:d}'.format(
                    t0=video_data.TIME_VIDEO_END.time - 10,
                    t1=video_data.TIME_VIDEO_END.time,
                    distance=np.interp(
                        video_data.TIME_VIDEO_END.time,
                        three_dist_arrays[i][:, 0],
                        three_dist_arrays[i][:, 1],
                    ),
                    lt=i+1,
                ) for i in range(len(three_dist_arrays))
            ]
        )
        plot_data.extend(
            [
                # label 10 "2770m" at 23,2770 right font ",10" # rotate by 45
                'set label "{distance:.0f}m" at {t:.1f},{distance:.1f} right font ",10"'.format(
                    t=video_data.TIME_VIDEO_END.time - 10 - 1,
                    distance=np.interp(
                        video_data.TIME_VIDEO_END.time,
                        three_dist_arrays[i][:, 0],
                        three_dist_arrays[i][:, 1],
                    ),
                ) for i in range(len(three_dist_arrays))
            ]
        )
    return plot_data


def gnuplot_distance_plt() -> str:
    return _gnuplot_distance_plt().replace(
        '# set_yrange', 'set yrange [-1500:4000]'
    ).replace(
        '# set_title', 'set title "Distance from t=0 and projected backward to v=0."'
    )


def gnuplot_distance_runway_end_plt() -> str:
    return _gnuplot_distance_plt().replace(
        '# set_yrange', 'set yrange [*:*]'
    ).replace(
        '# set_title', 'set title "Distance from runway start."'
    )


def _gnuplot_distance_plt() -> str:
    return """# set logscale x
set colorsequence classic
set grid
# set_title
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance (m)"
# set_yrange
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
plot "{file_name}.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \\
    "{file_name}.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \\
    "{file_name}.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
"""


def gnuplot_distance_from_transits(stream: typing.TextIO=sys.stdout) -> typing.List[str]:
    """
    Creates the data that compares distance computed by integrating ground speed with
    transit data.
    """
    print()
    print('TRACE: Distance fit from transits:', video_analysis.distance_fit_from_transits())

    notes = [
        'Distance of aircraft down the runway from comparing integrated ground speed and transit lines.',
        'time x_transit(m) x_min(m) x_mid(m) x_max(m) x_transit(m)',
    ]
    if len(notes):
        stream.write('#\n')
        stream.write('# Notes:\n')
        for note in notes:
            stream.write('# {}\n'.format(note))

    # Get the min/mid/max ground speed fits
    offset_distance_at_t = video_data.TIME_VIDEO_END_ASPHALT.time
    gs_fits = [plot_common.get_gs_fit(err) for err in video_data.ErrorDirection]
    offsets = [
        video_data.RUNWAY_LEN_M - video_analysis.ground_speed_integral(0, offset_distance_at_t, gs_fit)
        for gs_fit in gs_fits
    ]
    # Establish observer
    observer_xy_start_runway = plot_common.observer_xy()

    result = []
    for event in video_analysis.transit_x_axis_distances(*observer_xy_start_runway):
        stream.write(
            '{t:<6.1f} {d_transit:.1f} {d_min:.1f} {d_mid:.1f} {d_max:.1f} # "{label:}"'.format(
                t=event.time,
                d_transit=event.distance,
                d_min=video_analysis.ground_speed_integral(0.0, event.time, gs_fits[0]) + offsets[0],
                # 1182 metres
                d_mid=video_analysis.ground_speed_integral(0.0, event.time, gs_fits[1]) + offsets[1],
                d_max=video_analysis.ground_speed_integral(0.0, event.time, gs_fits[2]) + offsets[2],
                label=event.label,
            )
        )
        stream.write('\n')
        d = event.distance - video_analysis.ground_speed_integral(0.0, event.time, gs_fits[1]) + 3 - plot_common.x_offset()
        result.append(
            'set label "{label:} t={t:.1f}s ∆d={d:.0f}" at {t:.1f},{d:.1f} right font ",6" rotate by -35'.format(
                label=event.label,
                t=event.time - 0.5,
                d=d
            )
        )
    return result


def gnuplot_distance_from_transits_plt() -> str:
    return """# set logscale x
set colorsequence classic
set grid
set title "Distances down runway comparing estimates with transits."
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance Compared to Mid Estimate (m)"
set yrange [-150:100]
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
set key box
#  lw 2 pointsize 2

{computed_data}

# linespoints
#plot "{file_name}.dat" using 1:($3-$4) title "Mid estimate -10 knots" lt 1 lw 1.5 w lines, \\
    "{file_name}.dat" using 1:($4-$4) title "Mid estimate" lt 2 lw 1.5 w lines, \\
    "{file_name}.dat" using 1:($5-$4) title "Mid estimate +10 knots" lt 3 lw 1.5 w lines, \\
    "{file_name}.dat" using 1:($2-$4) title "From transits" lt 2 lw 1.5 ps 1.25 w points
plot "{file_name}.dat" using 1:($4-$4) title "Mid estimate" lt 2 lw 1.5 w lines, \\
    "{file_name}.dat" using 1:($2-$4) title "From transits" lt 3 lw 1.5 ps 1.25 w points, \\
    "{file_name}.dat" using 1:(0.5*($5-$4)) title "Mid estimate +5 knots" lt 3 lw 1.5 w lines, \\
    "{file_name}.dat" using 1:(0.5*($5-$4)+25) title "Mid estimate +5 knots +25m" lt 1 lw 1.0 w lines, \\
    "{file_name}.dat" using 1:(0.5*($5-$4)-25) title "Mid estimate +5 knots -25m" lt 1 lw 1.0 w lines
reset
"""


def markdown_table_aircraft_start() -> typing.Tuple[typing.List[str], str]:
    """
    Returns a markdown table and a title for the distance estimates at start of take off.
    """
    ret = [
        '| Calculation | Video Time t (s) | Distance from start of Runway (m) | Distance from start of Runway at t=0 (m) |',
        '| --- | --: | --: | --: |',
    ]
    labels = (
        'Mid speed -10 knots',
        'Mid speed',
        'Mid speed +10 knots',
    )
    three_dist_arrays = get_distances_min_mid_max(video_data.TIME_VIDEO_END_ASPHALT.time)
    # Time ranges for min/mid/max of start of take off
    t_range = [arr[0][0] for arr in three_dist_arrays]
    # Distance of start of take off from start of runway for min/mid/max
    d_range = [arr[0][1] for arr in three_dist_arrays]
    # Distance of start of video from start of runway for min/mid/max
    d_range_video_start = [
        video_utils.interpolate(arr[:, 0], arr[:, 1], 0.0) for arr in three_dist_arrays
    ]
    for label, arr, d_video_start in zip(labels, three_dist_arrays, d_range_video_start):
        t, d = arr[0]
        ret.append(
            '| {} | {:.1f} | {:.0f} | {:.0f} |'.format(
                label, t, d, d_video_start
            )
        )
    ret.append(
        '| **{}** | **{:.1f} ±{:.1f}** | **{:.0f} ±{:.0f}** | **{:.0f} ±{:.0f}** |'.format(
            'Range and worst error',
            t_range[1], max(abs(t_range[2] - t_range[1]), abs(t_range[0] - t_range[1])),
            d_range[1], max(abs(d_range[2] - d_range[1]), abs(d_range[0] - d_range[1])),
            d_range_video_start[1],
            max(abs(d_range_video_start[2] - d_range_video_start[1]), abs(d_range_video_start[0] - d_range_video_start[1])),
        )
    )
    return ret, 'Distance Estimates for the Start of Take off'
