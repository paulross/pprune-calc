import collections
import typing

import numpy as np

from analysis import video_analysis
from analysis import video_data
from analysis import video_utils
from analysis.plot_common import get_gs_fits_corrected
from analysis.plot_svg import EVENTS_TIMED


def create_event_table_header() -> typing.List[str]:
    return [
        'Event',
        'Video Time (s)',
        'Time from Start Take Off (s)',
        'Ground Speed (knots)',
        'Acceleration (knots/s)',
        'From Start of Runway (m)',
        'To end Asphalt (m)',
        'Notes',
    ]


ValueAndError = collections.namedtuple('ValueAndError', 'value, error')


class ComputedEventData(
    collections.namedtuple(
        'ComputedEventData',
        'label, t_video, t_start, ground_speed, acceleration, d_start, d_end, notes'
    )
):

    def __str__(self):
        """
        Stringify events, example::

            Start of take off : t=-32.8 ± 2.8 [ 0.0 ± 2.8] d= 232.3 ± 312.1 d_end=3007.7 ± 312.1 Estimated
            Video starts      : t=  0.0 ± 0.0 [32.8 ± 0.0] d=1181.6 ± 143.1 d_end=2058.4 ± 143.1
            Nose wheel off    : t= 17.9 ± 0.0 [50.7 ± 0.0] d=2400.1 ±  51.0 d_end= 839.9 ±  51.0 Rotation of ~1.4 °/s to t=23
            Main wheels off   : t= 25.6 ± 0.0 [58.5 ± 0.0] d=3047.5 ±  11.2 d_end= 192.5 ±  11.2
            End asphalt       : t= 27.8 ± 0.0 [60.6 ± 0.0] d=3240.0 ±   0.0 d_end=   0.0 ±   0.0 Defined datum
            Video ends        : t= 33.7 ± 0.0 [66.5 ± 0.0] d=3782.7 ±  30.2 d_end=-542.7 ±  30.2
        """
        return (
            '{label:18}:'
            ' t={t_video:5.1f} ± {t_video_err:3.1f}'
            ' [{t_start:4.1f} ± {t_start_err:3.1f}]'
            ' gs={gs:4.1f} ±{gs_err:3.1f}'
            ' d={d_start:6.1f} ± {d_start_err:5.1f}'
            ' d_end={d_end:6.1f} ± {d_end_err:5.1f}'
            ' {notes}'.format(
                label=self.label,
                t_video=self.t_video.value,
                t_video_err=self.t_video.error or 0.0,
                t_start=self.t_start.value,
                t_start_err=self.t_start.error or 0.0,
                gs=self.ground_speed.value,
                gs_err=self.ground_speed.error or 0.0,
                d_start=self.d_start.value,
                d_start_err=self.d_start.error,
                d_end=self.d_end.value,
                d_end_err=self.d_end.error,
                notes=self.notes,
            )
        )


def gen_event_data() -> ComputedEventData:
    # gs_fits = [plot_common.get_gs_fit(err) for err in video_data.ErrorDirection]
    gs_fits  = get_gs_fits_corrected()
    # Find initial start and distance
    start_times = [np.roots(list(reversed(v)))[-1] for v in gs_fits]
    # These are the location of the aircraft from the beginning of the runway at t=0
    offsets = [
        video_data.RUNWAY_LEN_M - video_analysis.ground_speed_integral(
            0, video_data.TIME_VIDEO_END_ASPHALT.time, gs_fit
        )
        for gs_fit in gs_fits
    ]
    gs_fit_mid = gs_fits[1]
    for event in EVENTS_TIMED:
        t_video = event.t
        if t_video is None:
            # Compute t_video from estimated start
            t_video = start_times[1]
            t_start = 0.0
            t_err = max([abs(start_times[1] - start_times[0]), abs(start_times[1] - start_times[2])])
            gs_err = None
        else:
            t_start = t_video - start_times[1]
            t_err = None
            gs_err = video_utils.knots_to_m_p_s(5.0)#max([abs(v) for v in GROUND_SPEED_OFFSETS])
        gs = video_analysis.ground_speed_from_fit(t_video, gs_fit_mid)
        accl = video_analysis.ground_speed_differential(t_video, gs_fit_mid)
        d_from_start = offsets[1] + video_analysis.ground_speed_integral(0.0, t_video, gs_fits[1])
        d_from_start_min = offsets[0] + video_analysis.ground_speed_integral(0.0, t_video, gs_fits[0])
        d_from_start_max = offsets[2] + video_analysis.ground_speed_integral(0.0, t_video, gs_fits[2])
        d_from_start_error = max(
            [
                abs(d_from_start - d_from_start_min),
                abs(d_from_start - d_from_start_max),
            ]
        )
        # Transit calculations improve integrated distance
        if t_video >= 0.0:
            d_from_start_error = 25.0
        d_from_start_error = max([d_from_start_error, 25.0])
        yield ComputedEventData(
            event.label,
            ValueAndError(t_video, t_err),
            ValueAndError(t_start, t_err),
            ValueAndError(gs, gs_err),
            ValueAndError(accl, 0.17 / 2), # Hard coded
            ValueAndError(d_from_start, d_from_start_error),
            ValueAndError(video_data.RUNWAY_LEN_M - d_from_start, d_from_start_error),
            event.notes,
        )


def create_event_table() -> typing.List[typing.List[str]]:
    table = []
    # Take the t_start error at the beginning and propagate it.
    t_start_error = None
    for event in gen_event_data():
        # print('TRACE: event', event)
        # 'label, t_video, t_start, ground_speed, acceleration, d_start, d_end, notes'
        if event.t_start.error is not None:
            t_start_error = event.t_start.error
        row = [
            event.label,
            # t_video
            '{:.1f} ±{:.1f}'.format(
                event.t_video.value, event.t_video.error
            ) if event.t_video.error is not None else '{:.1f}'.format(event.t_video.value),
            # t_start
            '{:.1f} ±{:.1f}'.format(
                event.t_start.value, t_start_error
            ),
            # ground speed
            '{:.0f} ±{:.0f}'.format(
                video_utils.m_p_s_to_knots(event.ground_speed.value),
                video_utils.m_p_s_to_knots(event.ground_speed.error)
            ) if event.ground_speed.error is not None else '{:.0f}'.format(
                video_utils.m_p_s_to_knots(event.ground_speed.value)),
            '{:.1f} ±{:0.2f}'.format(
                video_utils.m_p_s_to_knots(event.acceleration.value),
                video_utils.m_p_s_to_knots(event.acceleration.error),
            ),
            '{:.0f} ±{:.0f}'.format(event.d_start.value, event.d_start.error),
            '{:.0f} ±{:.0f}'.format(event.d_end.value, event.d_end.error),
            event.notes,
        ]
        table.append(row)
    return table


def print_event_table_markdown():
    table, title = markdown_table_of_events()
    print(title)
    print('\n'.join(table))


def markdown_table_of_events() -> typing.Union[typing.List[str], str]:
    def expand_line(lst: typing.List[str]) -> str:
        return '| {} |'.format(' | '.join(lst))

    ret = [
        expand_line(create_event_table_header()),
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |',
    ]
    for row in create_event_table():
        ret.append(expand_line(row))
    return ret, 'Selected Events'