import collections
import typing

import numpy as np

from analysis import plot_constants
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
    EventTimed(video_data.TIME_VIDEO_END_ASPHALT.time, 'End asphalt', 'Defined datum'),
    EventTimed(video_data.TIME_VIDEO_END.time, 'Video ends', ''),
)


def create_svg_observer_xy(d_video_starts: float, d_video_starts_error: float) -> typing.List[str]:
    """
    Returns a list of SVG strings for the estimated observer position.
    """
    observer_xy, _possible = video_analysis.observer_position_combinations(
        baseline=plot_constants.OBSERVER_XY_MINIMUM_BASELINE,
        ignore_first_n = plot_constants.OBSERVER_XY_IGNORE_N_FIRST_BEARINGS,
    )
    result = ['<!-- {} -->'.format('create_svg_observer_xy()'.center(75))]
    # =========== Write dots
    dot_radius = plot_constants.distance_m_to_pixels(15)
    for i in range(len(observer_xy)):
        pos_xy = plot_constants.PosXY(observer_xy[i, 0] + d_video_starts, observer_xy[i, 1])
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
    mean_x = np.mean(observer_xy[:, 0])
    mean_y = np.mean(observer_xy[:, 1])
    range_x = np.max(observer_xy[:, 0]) - np.min(observer_xy[:, 0])
    range_y = np.max(observer_xy[:, 1]) - np.min(observer_xy[:, 1])
    radius_m = max(range_x, range_y) / 2
    radius_m = 75
    circle_pos = plot_constants.position_m_to_pixels(plot_constants.PosXY(mean_x + d_video_starts, mean_y))
    result.append(
        '<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="magenta" stroke-width="4" fill="none" />'.format(
            cx=circle_pos.x,
            cy=circle_pos.y,
            r=plot_constants.distance_m_to_pixels(radius_m),
        )
    )
    # Add label and line
    label_offset = 60
    result.append(
        '<text x="{x:.1f}" y="{y:.1f}" fill="magenta" text-anchor="{text_anchor:}"' \
        ' alignment-baseline="bottom" font-family="Helvetica" font-size="20" font-weight="bold">{text:}</text>'.format(
            x=circle_pos.x, y=circle_pos.y-label_offset, text='Probable location of observer', text_anchor='middle'
        )
    )
    result.append(
        '<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="magenta" stroke-width="4" />'.format(
            x1=circle_pos.x, y1=circle_pos.y-label_offset,
            x2=circle_pos.x, y2=circle_pos.y - plot_constants.distance_m_to_pixels(radius_m),
        )
    )
    result.append('<!-- DONE {} -->'.format('create_svg_observer_xy()'.center(75)))
    return result

def create_svg_transit_to_observer_xy() -> typing.List[str]:
    """
    Returns a list of SVG strings for the transit lines to the estimated observer position.
    """
    result = []
    # TODO: Finish this
    return result


def create_svg() -> typing.List[str]:
    label_offset = 50
    result = []
    d_video_starts = None
    d_video_starts_error = None
    for event in plot_events.gen_event_data():
        # 'label, t_video, t_start, ground_speed, acceleration, d_start, d_end, notes'
        if event.t_video.value == 0.0:
            # Grab the distance of the video start and the distance error
            d_video_starts = event.d_start.value
            d_video_starts_error = event.d_start.error
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
        text = event.label + ': {v:.0f} knots, t={t_video:0.1f} [{t_start:0.1f}]'.format(
            v=video_utils.m_p_s_to_knots(event.ground_speed.value),
            t_video=event.t_video.value,
            t_start=event.t_start.value
        )
        result.append(
            '<text x="{x:.1f}" y="{y:.1f}" fill="blue" text-anchor="{text_anchor:}"'\
            ' alignment-baseline="middle" font-family="Helvetica" font-size="20"'\
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
    result.extend(create_svg_observer_xy(d_video_starts, d_video_starts_error))
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