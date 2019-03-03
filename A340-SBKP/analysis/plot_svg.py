import collections
import math
import typing

import numpy as np

from analysis import plot_constants, plot_common
from analysis import plot_events
from analysis import video_analysis
from analysis import video_data
from analysis import video_utils


def polygon_string(xy: plot_constants.PosXY,
                   dx: float,
                   dy: float,
                   fill: str,
                   stroke: str,
                   stroke_width: int) -> str:
    # <polygon fill="red" stroke="blue" stroke-width="10"
    #             points="350,75  379,161 469,161 397,215
    #                     423,301 350,250 277,301 303,215
    #                     231,161 321,161" />
    points = [
        plot_constants.position_m_to_pixels(plot_constants.PosXY(xy.x + dx, xy.y + dy)),
        plot_constants.position_m_to_pixels(plot_constants.PosXY(xy.x - dx, xy.y + dy)),
        plot_constants.position_m_to_pixels(plot_constants.PosXY(xy.x - dx, xy.y - dy)),
        plot_constants.position_m_to_pixels(plot_constants.PosXY(xy.x + dx, xy.y - dy)),
    ]
    point_str = ' '.join(['{:.1f},{:.1f}'.format(p.x, p.y) for p in points])
    result = '<polygon fill="{fill:}" stroke="{stroke:}" stroke-width="{stroke_width:d}" points="{points:}" />'.format(
        fill=fill,
        stroke=stroke,
        stroke_width=stroke_width,
        points=point_str,
    )
    return result


SvgEvent = collections.namedtuple('SvgEvent', 't, label')
SVG_EVENTS = (
    SvgEvent(
        None,
        'Estimated start of take off: v={v:.0f}, t={t_video:.0f} [{t_start:.0f}]'
    ),
    SvgEvent(
        0.0,
        'Video starts: v={v:.0f}, t={t_video:.0f} [{t_start:.0f}]'
    ),
    SvgEvent(
        video_data.TIME_VIDEO_NOSEWHEEL_OFF.time,
        'Nose wheel off: v={v:.0f}, t={t_video:.0f} [{t_start:.0f}]'
    ),
    SvgEvent(
        video_data.TIME_VIDEO_MAINWHEEL_OFF.time,
        'Main wheels off: v={v:.0f}, t={t_video:.0f} [{t_start:.0f}]'
    ),
    SvgEvent(
        video_data.TIME_VIDEO_END_ASPHALT.time,
        'End asphalt: v={v:.0f}, t={t_video:.0f} [{t_start:.0f}]'
    ),
    SvgEvent(
        video_data.TIME_VIDEO_END.time,
        'Video ends: v={v:.0f}, t={t_video:.0f} [{t_start:.0f}]'
    ),
)
EventTimed = collections.namedtuple('SvgEvent', 't, label, notes')
EVENTS_TIMED = (
    # Single special case, start time has to be computed.
    EventTimed(None, 'Start of take off', 'Estimated'),
    EventTimed(0.0, 'Video starts', ''),
    EventTimed(video_data.TIME_VIDEO_NOSEWHEEL_OFF.time, 'Nose wheel off', 'Rotation of ~1.4 °/s to t=23'),
    EventTimed(video_data.TIME_VIDEO_MAINWHEEL_OFF.time, 'Main wheels off', ''),
    EventTimed(video_data.TIME_VIDEO_END_ASPHALT.time, 'End asphalt', 'Used as a datum for some calculations.'),
    EventTimed(video_data.TIME_VIDEO_END.time, 'Video ends', ''),
)


def create_svg_observer_xy(d_video_starts: float, d_video_starts_error: float) -> typing.List[str]:
    """
    Returns a list of SVG strings for the estimated observer position.
    """
    obs_xy_spects, _possible = video_analysis.observer_position_combinations_from_aspects(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n = plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
        t_range=plot_constants.OBSERVER_XY_TIME_RANGE,
    )
    ((obs_x_transit, _x_std), (obs_y_transit, _y_std)) = video_analysis.observer_position_mean_std_from_full_transits()
    result = ['<!-- {} -->'.format('create_svg_observer_xy()'.center(75))]
    # =========== Write dots
    dot_radius = plot_constants.distance_m_to_pixels(10)
    for i in range(len(obs_xy_spects)):
        pos_xy = plot_constants.PosXY(obs_xy_spects[i, 0] + d_video_starts, obs_xy_spects[i, 1])
        pos_centre = plot_constants.position_m_to_pixels(pos_xy)
        result.append(
            '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="green" stroke-width="0.25" fill="cyan" />'.format(
                cx=pos_centre.x, cy=pos_centre.y, r=dot_radius,
            )
        )
        # pos_xy = plot_constants.PosXY(observer_xy[i, 0] + d_video_starts - d_video_starts_error, observer_xy[i, 1])
        # pos_centre = position_m_to_pixels(pos_xy)
        # result.append(
        #     '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="black" stroke-width="0.5" fill="red" />'.format(
        #         cx=pos_centre.x, cy=pos_centre.y, r=dot_radius,
        #     )
        # )
        # pos_xy = plot_constants.PosXY(observer_xy[i, 0] + d_video_starts + d_video_starts_error, observer_xy[i, 1])
        # pos_centre = position_m_to_pixels(pos_xy)
        # result.append(
        #     '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="black" stroke-width="0.5" fill="yellow" />'.format(
        #         cx=pos_centre.x, cy=pos_centre.y, r=dot_radius,
        #     )
        # )
    # Calculate the mean position and the radius from the extremes.
    print('TRACE: d_video_starts: {}'.format(d_video_starts))
    print('TRACE: bearing x: {} y: {}'.format(
        np.mean(obs_xy_spects[:, 0]) + d_video_starts,
        np.mean(obs_xy_spects[:, 1]),
    ))
    print('TRACE: transit x: {} y: {}'.format(obs_x_transit, obs_y_transit))
    # mean_x = np.mean(obs_xy_spects[:, 0])
    # mean_y = np.mean(obs_xy_spects[:, 1])
    # range_x = np.max(observer_xy[:, 0]) - np.min(observer_xy[:, 0])
    # range_y = np.max(observer_xy[:, 1]) - np.min(observer_xy[:, 1])
    # radius_m = max(range_x, range_y) / 2
    result.append('<!-- DONE {} -->'.format('create_svg_observer_xy()'.center(75)))
    return result


def create_svg_observer_annotation() -> typing.List[str]:
    ((obs_x_transit, _x_std), (obs_y_transit, _y_std)) = video_analysis.observer_position_mean_std_from_full_transits()
    result = [
        '<!-- {} -->'.format('create_svg_observer_annotation()'.center(75)),
    ]
    radius_m = 25 # 100
    circle_pos = plot_constants.position_m_to_pixels(plot_constants.PosXY(
        obs_x_transit, obs_y_transit
    ))
    result.append(
        '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="magenta" stroke-width="3" fill="none" />'.format(
            cx=circle_pos.x,
            cy=circle_pos.y,
            r=plot_constants.distance_m_to_pixels(radius_m),
        )
    )
    # Add label and line
    label_offset = 100
    result.append(
        '<text x="{x:.1f}" y="{y:.1f}" fill="magenta" text-anchor="{text_anchor:}"' \
        ' alignment-baseline="bottom" font-family="Helvetica" font-size="14" font-weight="bold">{text:}</text>'.format(
            x=circle_pos.x, y=circle_pos.y-label_offset, text='Probable location of observer', text_anchor='middle'
        )
    )
    result.append(
        '<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="magenta" stroke-width="3" />'.format(
            x1=circle_pos.x, y1=circle_pos.y-label_offset+2,
            x2=circle_pos.x, y2=circle_pos.y - plot_constants.distance_m_to_pixels(radius_m),
        )
    )
    result.append('<!-- DONE: {} -->'.format('create_svg_observer_annotation()'.center(75)))
    return result


def create_svg_transit_to_observer_xy() -> typing.List[str]:
    """
    Returns a list of SVG strings for the transit lines to the estimated observer position.
    """
    result = []
    # TODO: Have a common API for observer postion
    observer_xy_array, _possible = video_analysis.observer_position_combinations_from_aspects(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n = plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
    )
    observer_xy = video_utils.XY(
        np.mean(observer_xy_array[:, 0]) + plot_common.x_offset(),
        np.mean(observer_xy_array[:, 1])
    )

    result.append('<!-- {} -->'.format('create_svg_transit_to_observer_xy()'.center(75)))
    colour = 'black'
    radius = plot_constants.distance_m_to_pixels(15)
    for transit_line in video_data.GOOGLE_EARTH_FULL_TRANSITS:
        x_0, y_0 = transit_line.frm.xy
        circle_pos_0 = plot_constants.position_m_to_pixels(plot_constants.PosXY(x_0, y_0))
        result.append(
            '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="{colour:}" stroke-width="1" fill="none" />'.format(
                colour=colour,
                cx=circle_pos_0.x,
                cy=circle_pos_0.y,
                r=radius,
            )
        )
        x_1, y_1 = transit_line.to.xy
        circle_pos_1 = plot_constants.position_m_to_pixels(plot_constants.PosXY(x_1, y_1))
        result.append(
            '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="{colour:}" stroke-width="1" fill="none" />'.format(
                colour=colour,
                cx=circle_pos_1.x,
                cy=circle_pos_1.y,
                r=radius,
            )
        )
        end_point = video_utils.transit_line_past_observer(
            transit_line.frm.xy, transit_line.to.xy, observer_xy, 250.0
        )
        # print('TRACE: create_svg_transit_to_observer_xy():', end_point)
        circle_pos_2 = plot_constants.position_m_to_pixels(end_point)
        result.append(
            '<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour:}" stroke-width="1" />'.format(
                colour=colour,
                x1=circle_pos_0.x, y1=circle_pos_0.y,
                x2=circle_pos_2.x, y2=circle_pos_2.y,
            )
        )
    result.append('<!-- DONE {} -->'.format('create_svg_transit_to_observer_xy()'.center(75)))
    return result


def create_svg() -> typing.List[str]:
    label_offset = 50
    result = []
    d_video_starts = 1110
    d_video_starts_error = None
    for event in plot_events.gen_event_data():
        # TODO: Add distance information in metres to labels of the form:
        # 'from_start [from_end]'
        # 'label, t_video, t_start, ground_speed, acceleration, d_start, d_end, notes'
        # if event.t_video.value == 0.0:
        #     # Grab the distance of the video start and the distance error
        #     d_video_starts = event.d_start.value
        #     d_video_starts_error = event.d_start.error
        xy_in_m = plot_constants.PosXY(event.d_start.value, 0.0)
        event_dx = event.d_start.error
        result.append(polygon_string(xy_in_m, event_dx, 25, 'red', 'blue', 1))
        pos = plot_constants.position_m_to_pixels(xy_in_m)
        if pos.x < 650:
            # Label right
            x = pos.x + label_offset
            text_anchor = 'start'
        else:
            # Label left
            x = pos.x - label_offset
            text_anchor = 'end'
        text = event.label + ': v={v:.0f} knots, t={t_video:0.1f}s [{t_start:0.1f}s] d={d_start:0.0f}m [{d_end:0.0f}m to go]'.format(
            v=video_utils.m_p_s_to_knots(event.ground_speed.value),
            t_video=event.t_video.value,
            t_start=event.t_start.value,
            d_start=xy_in_m.x,
            d_end=video_data.RUNWAY_LEN_M-xy_in_m.x,
        )
        result.append(
            '<text x="{x:.1f}" y="{y:.1f}" fill="blue" text-anchor="{text_anchor:}"'\
            ' alignment-baseline="middle" font-family="Helvetica" font-size="14"'\
            ' font-weight="bold">{text:}</text>'.format(
                x=x, y=pos.y, text=text, text_anchor=text_anchor
            )
        )
        result.append(
            '<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" style="stroke:rgb(255,255,0);stroke-width:4" />'.format(
                x1=pos.x, y1=pos.y, x2=x, y2=pos.y
            )
        )
        # Add a yellow circle
        result.append(
            '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="black" stroke-width="1" fill="yellow" />'.format(
                cx=pos.x, cy=pos.y, r=3,
            )
        )
    # result.extend(create_svg_observer_xy(d_video_starts, d_video_starts_error))
    result.extend(create_svg_observer_annotation())
    result.extend(create_svg_transit_to_observer_xy())
    return result


def modify_svg_as_text_and_copy(infile: str, outfile: str):
    with open(infile) as fin:
        with open(outfile, 'w') as fout:
            for line in fin.readlines():
                if line == '</svg>\n':
                    # Insert lines
                    for out_line in create_svg():
                        fout.write(out_line)
                        fout.write('\n')
                fout.write(line)