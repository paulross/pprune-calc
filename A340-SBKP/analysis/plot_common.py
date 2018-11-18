import itertools
import os
import subprocess
import sys
import typing

import numpy as np

from analysis import plot_constants, video_data, video_utils, video_analysis
from analysis import video_analysis


def gnuplot_write_arrays(stream: typing.TextIO=sys.stdout,
                         *args: np.ndarray) -> None:
    # Requires arg[:, 0] to be ordered.
    times = set()
    for arg in args:
        if arg.ndim != 2:
            raise ValueError('Arrays must be 2D not shape: {}'.format(arg.shape))
        times |= set(arg[:,0])
    timebase = sorted(times)
    indices = [0,] * len(args)
    for t in timebase:
        part_line = [
            '{:<8.1f}'.format(t)
        ]
        for i_arg, arg in enumerate(args):
            i = indices[i_arg]
            if i < len(arg) and arg[i, 0] == t:
                part_line.extend(
                    ['{:8.3f}'.format(arg[i, j]) for j in range(1, arg.shape[1])]
                )
                indices[i_arg] += 1
            else:
                part_line.extend(
                    ['{:8s}'.format('NaN') for j in range(1, arg.shape[1])]
                )
        stream.write(' '.join(part_line))
        stream.write('\n')


__GROUND_SPEED_FITS: typing.Dict[video_data.ErrorDirection, typing.List[float]] = {}


def get_gs_fit(err: video_data.ErrorDirection) -> typing.List[float]:
    if err not in __GROUND_SPEED_FITS:
        if err == video_data.ErrorDirection.MIN:
            __GROUND_SPEED_FITS[err] = video_analysis.ground_speed_curve_fit_with_offset(
                plot_constants.GROUND_SPEED_OFFSETS[0]
            )
        elif err == video_data.ErrorDirection.MID:
            __GROUND_SPEED_FITS[err] = video_analysis.ground_speed_curve_fit_with_offset(
                plot_constants.GROUND_SPEED_OFFSETS[1]
            )
        elif err == video_data.ErrorDirection.MAX:
            __GROUND_SPEED_FITS[err] = video_analysis.ground_speed_curve_fit_with_offset(
                plot_constants.GROUND_SPEED_OFFSETS[2]
            )
        else:
            assert 0
    return __GROUND_SPEED_FITS[err]



def plot_file(name: str) -> str:
    if name == '':
        return os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, 'plots'))
    return os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, 'plots', name))


def write_dat_plt_call(name: str, fn_dat: typing.Callable, fn_plt: typing.Callable) -> None:
    """
    Create the plot for name.
    fn_data is a function that takes a stream and writes the 'name.dat' file. This must return
    a list of strings, if non-empty then they are written into the plt file as {computed_data}.
    fn_plot is a function that return the 'name.plt' string ready to insert the 'name.dat'
    into the format variable 'file_name'.
    """
    print('Writing "{}"'.format(name))
    with open(plot_file('{}.dat'.format(name)), 'w') as outfile:
        computed_data_strings = fn_dat(outfile)
    if len(computed_data_strings):
        plot_data = fn_plt().format(
            file_name=name, computed_data='\n'.join(computed_data_strings)
        )
    else:
        plot_data = fn_plt().format(file_name=name)
    plt_file_path = plot_file('{}.plt'.format(name))
    with open(plt_file_path, 'w') as outfile:
        outfile.write(plot_data)
    proc = subprocess.Popen(
        args=['gnuplot', '-p', os.path.basename(plt_file_path)],
        shell=False,
        cwd=os.path.dirname(plt_file_path),
    )
    try:
        outs, errs = proc.communicate(timeout=1)
    except subprocess.TimeoutExpired as err:
        print('ERROR:', err)
        proc.kill()
        outs, errs = proc.communicate()
    # print(outs, errs, proc.returncode)


def observer_xy_with_std_from_aspects():
    """
    Returns ((observer_x_mean, observer_x_std), (observer_y_mean, observer_y_std))
    in metres from aircraft aspects.
    """
    return video_analysis.observer_position_mean_std_from_aspects(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n=plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )


def x_offset():
    """The x offset at t=0 from the runway start based on integrating the ground speed integral."""
    distance_to_end = video_analysis.ground_speed_integral(
        0,
        video_data.TIME_VIDEO_END_ASPHALT.time,
        get_gs_fit(video_data.ErrorDirection.MID)
    )
    result = video_data.RUNWAY_LEN_M - distance_to_end
    return result


def observer_xy():
    """Returns (x, y) in metres from start of runway."""
    # ((observer_x_mean, observer_x_std), (observer_y_mean, observer_y_std)) = observer_xy_with_std_from_aspects()
    ((observer_x_mean, observer_x_std), (observer_y_mean, observer_y_std)) = \
        video_analysis.observer_position_mean_std_from_full_transits()
    observer_xy_start_runway = observer_x_mean, observer_y_mean
    return observer_xy_start_runway


def full_transit_labels_and_arrows(arrow_rgb: str, line_width: float) -> typing.List[str]:
    """
    Returns a list of gnuplot directives that are lines between the from/to full transit points
    and labels the from/to points.
    """
    ret = []
    observer = video_utils.XY(*observer_xy())
    for transit_line in video_data.GOOGLE_EARTH_FULL_TRANSITS:
        # Compute a position past the observer
        end_point = video_utils.transit_line_past_observer(
            transit_line.frm.xy, transit_line.to.xy, observer, 250.0
        )
        # Line between from/to points
        ret.append(
            'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw {lw:0.2f} lc rgb "{arrow_rgb}"'.format(
                x0=transit_line.frm.xy.x,
                y0=transit_line.frm.xy.y,
                x1=end_point.x,
                y1=end_point.y,
                arrow_rgb=arrow_rgb,
                lw=line_width,
            )
        )
        # Label from point
        ret.append(
            'set label "{label:}" at {x:.1f},{y:.1f} right font ",9" rotate by -30'.format(
                label=transit_line.frm.label,
                x=transit_line.frm.xy.x - 50,
                y=transit_line.frm.xy.y,
            )
        )
        # Label to point
        ret.append(
            'set label "{label:}" at {x:.1f},{y:.1f} right font ",9" rotate by -30'.format(
                label=transit_line.to.label,
                x=transit_line.to.xy.x - 50,
                y=transit_line.to.xy.y,
            )
        )
    return ret


def full_transit_arrows_with_position_error(arrow_rgb: str,
                                            error: typing.Union[int, float],
                                            line_width: float) -> typing.List[str]:
    """
    Returns a list of gnuplot directives that are lines between the from/to full transit points
    with the given positional error.
    """
    ret = []
    observer = video_utils.XY(*observer_xy())
    for transit_line in video_data.GOOGLE_EARTH_FULL_TRANSITS:
        new_from, new_to, new_bearing = video_utils.transit_point_with_error(
            transit_line.frm.xy, transit_line.to.xy, error=error
        )
        end_point = video_utils.transit_line_past_observer(
            new_from, new_to, observer, 250.0
        )
        ret.append(
            'set arrow from {x0:.0f},{y0:.0f} to {x1:.0f},{y1:.0f} nohead lw {lw:0.2f} lc rgb "{arrow_rgb}" dt 4'.format(
                x0=new_from.x,
                y0=new_from.y,
                x1=end_point.x,
                y1=end_point.y,
                arrow_rgb=arrow_rgb,
                lw=line_width,
            )
        )
    return ret


def observer_position_from_full_transits():
    crossing_x = []
    crossing_y = []
    for num, (i, j) in enumerate(itertools.combinations(range(len(video_data.GOOGLE_EARTH_FULL_TRANSITS)), 2)):
        transit1: video_data.FullTransitLine = video_data.GOOGLE_EARTH_FULL_TRANSITS[i]
        transit2: video_data.FullTransitLine = video_data.GOOGLE_EARTH_FULL_TRANSITS[j]
        crossing = video_utils.intersect_two_lines(
            transit1.frm.xy, transit1.to.xy, transit2.frm.xy, transit2.to.xy,
        )
        crossing_x.append(crossing.x)
        crossing_y.append(crossing.y)
    return sum(crossing_x) / len(crossing_x), (max(crossing_x) - min(crossing_x)) / 2.0, \
        sum(crossing_y) / len(crossing_y), (max(crossing_y) - min(crossing_y)) / 2.0


def get_gs_fits_corrected() -> typing.List[typing.List[float]]:
    # Apply an offset of +5 knots and a tolerance of ±5knots
    gs_fits  = [
        video_analysis.ground_speed_curve_fit_with_offset(
            video_utils.knots_to_m_p_s(5.0 + -5.0)
        ),
        video_analysis.ground_speed_curve_fit_with_offset(
            video_utils.knots_to_m_p_s(5.0 + 0.0)
        ),
        video_analysis.ground_speed_curve_fit_with_offset(
            video_utils.knots_to_m_p_s(5.0 + 5.0)
        ),
    ]
    return gs_fits


def return_equations_of_motion() -> typing.List[str]:
    ret = []
    gs_fits  = get_gs_fits_corrected()
    ret.append('Ground speed (m/s) = {:.1f} {:+.2f} * t {:+.5f} * t^2 {:+.7f} * t^3'.format(*(gs_fits[1])))
    ret.append('Acceleration (m/s^2) = {:.2f} {:+.4f} * t {:+.6f} * t^2'.format(
        gs_fits[1][1],
        2 * gs_fits[1][2],
        3 * gs_fits[1][3],
    ))
    ret.append('Distance (m) = 1110 + {:.1f} * t {:+.3f} * t^2 {:+.5f} * t^3 {:+.7f} * t^4'.format(
        gs_fits[1][0],
        gs_fits[1][1] / 2.0,
        gs_fits[1][2] / 3.0,
        gs_fits[1][3] / 4.0,
    ))
    return ret



def markdown_table_equations_of_motion() -> typing.Tuple[typing.List[str], str]:
    """
    Returns equations of motion as a list of strings and the title in markdown format.

    For example::

        | Measure | Units | Formulae | Tolerance | Notes |
        | --- | --- | --- | --- | --- |
        | Ground speed | m/s | 58.3 + 1.48 * t - 0.00794 * t^2 - 0.0000418 * t^3 |  ±2.5 | See note 1 below. |
        | Acceleration | m/s^s | 1.48 - 0.0159 * t - 0.000125 * t^2 |  ±0.17 | See note 2 below. |
        | Distance | m | 1110 + 58.3 * t + 0.741 * t^2 - 0.00265 * t^3 - 0.0000104 * t^4 | ±25 for t>=0 | See note 3 below. |
    """
    ret = [
        '| Measure | Units | Formulae | Tolerance | Notes |',
        '| --- | --- | --- | --- | --- |',
    ]
    gs_fit = get_gs_fits_corrected()[1]
    offset_video_start = video_data.RUNWAY_LEN_M
    offset_video_start -= video_analysis.ground_speed_integral(
        0, video_data.TIME_VIDEO_END_ASPHALT.time, gs_fit
    )
    values = [gs_fit[i] for i in range(4)]
    ret.append(
        '| Ground speed | m/s | {:.2e} {:+.2e} * t {:+.2e} * t^2 {:+.2e} * t^3 | {} | {} |'.format(
            *values,
            '±2.5',
            'See note 1 below.',
        )
    )
    values = [i * gs_fit[i] for i in range(1, 4)]
    ret.append(
        '| Acceleration | m/s^2 | {:.2e} {:+.2e} * t {:+.2e} * t^2 | {} | {} |'.format(
            *values,
            '±0.17',
            'See note 2 below.',
        )
    )
    values = [offset_video_start]
    values += [gs_fit[i] / (i + 1) for i in range(4)]
    ret.append(
        '| Distance | m | {:.2e} + {:.2e} * t {:+.2e} * t^2 {:+.2e} * t^3 {:+.2e} * t^4 | {} | {} |'.format(
            *values,
            '±25 for t>=0',
            'See note 3 below.',
        ))
    return ret, 'Equations of Motion'


def get_distances_min_mid_max(offset_distance_at_t: float) -> typing.Tuple[np.ndarray]:
    """Returns a tuple of three np.ndarray of (time, distance) corresponding to the the
    -10, mid, +10 knot fits of ground speed.

    If offset_distance_at_t is non-zero an offset will be applied, that is the
    runway length - the distance at that offset time.
    So if the time is video_data.TIME_VIDEO_END_ASPHALT.time the distance is from the runway start.
    """
    gs_fits = [get_gs_fit(err) for err in video_data.ErrorDirection]
    three_dist_arrays = [] # Three different fits: -10, 0, +10 knots
    if offset_distance_at_t != 0.0:
        # Offsets of: [3240 - 1919, 3240 - 2058, 3240 - 2197,]
        offsets = [
            video_data.RUNWAY_LEN_M - video_analysis.ground_speed_integral(0, offset_distance_at_t, gs_fit)
                for gs_fit in gs_fits
        ]
    else:
        offsets = [0.0] * len(gs_fits)
    for i, gs_fit in enumerate(gs_fits):
        t = np.roots(list(reversed(gs_fit)))[-1]
        times = []
        while t < plot_constants.EXTRAPOLATED_RANGE.stop:
            times.append(t)
            t += 1
        # Add as special cases: t=0, t=27+24/30 - end of asphalt, t=end.
        for special_t in (
                0.0,
                video_data.TIME_VIDEO_NOSEWHEEL_OFF.time,
                video_data.TIME_VIDEO_MAINWHEEL_OFF.time,
                video_data.TIME_VIDEO_END_ASPHALT.time,
                video_data.TIME_VIDEO_END.time,
            ):
            if special_t not in times:
                times.append(special_t)
        array = []
        for t in sorted(times):
            array.append((t, video_analysis.ground_speed_integral(0, t, gs_fit) + offsets[i]))
        three_dist_arrays.append(np.array(array))
    return tuple(three_dist_arrays)