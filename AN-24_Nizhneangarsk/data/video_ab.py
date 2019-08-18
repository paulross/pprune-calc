"""
This is for data that links video A and video B together.
"""
import sys
import typing

import map_funcs
from common import structs
from data import video_a, video_b


# Map of events in video A to video B by respective frame number.
FRAME_TIE_DICT: typing.Dict[int, int] = {
    # First appearance in video B
    int(35.5 * 30): 36,
    # Tyre smoke
    1081: 42,
    # Increase in tyre smoke, no obvious event in video A.
    # 36 * 30: 96,
    # Start of large dust plume
    1384: 290,
    # Final impact
    1712: 23*25+1
}


def create_time_ties() -> typing.List[typing.Tuple[structs.TimeComment, structs.TimeComment]]:
    ret = []
    for frame_a in sorted(FRAME_TIE_DICT.keys()):
        t_a = video_a.frame_to_time(frame_a)
        t_b = video_b.frame_to_time(FRAME_TIE_DICT[frame_a])
        msg_a = video_a.FRAME_EVENTS[frame_a]
        msg_b = video_b.FRAME_EVENTS[FRAME_TIE_DICT[frame_a]]
        ret.append((structs.TimeComment(t_a, msg_a), structs.TimeComment(t_b, msg_b)))
    return ret


def time_differences() -> typing.List[float]:
    """Return the mean of the time difference, the point in video A when video B starts."""
    ties = create_time_ties()
    ret = [tie[0].time - tie[1].time for tie in ties]
    return ret


def time_difference_mid_max_min() -> structs.MidPlusMinus:
    """Returns the mid estimate of the time difference (t of video A at video B start) with the
    max and min estimate."""
    tds = time_differences()
    return structs.MidPlusMinus(sum(tds) / len(tds), max(tds), min(tds))


def print_video_a_video_b_ties():
    ties = create_time_ties()
    for tie in ties:
        # print(tie, tie[0].time - tie[1].time)
        print(
            f'{tie[0].time:6.1f} {tie[1].time:6.1f} {tie[0].time - tie[1].time:6.1f}'
            f' A: {tie[0].comment:40} <-> B: {tie[1].comment:40}'
        )
    mid_max_min = time_difference_mid_max_min()
    print(f'Mean (Ta - Tb): {mid_max_min.mid:.2f} ±{mid_max_min.tolerance:.1f} (s)')


def print_video_a_video_b_ties_markdown():
    """
| Time | Position | Ground Speed | Acceleration |
| :--: | :--: | :--: | :--: |
| 45.7 s | 1442 ±48 m | 60.0 ±3.7 m/s, 117 ±12 knots | -3.7 ±0.3 m/s^2 |
"""
    ties = create_time_ties()
    print('| Video B Event | Video B Time (s) | Video A Event | Video A Time (s) | Difference (s) |')
    print('| :-- | --: | :-- | --: | ---: |')
    for tie in ties:
        # print(tie, tie[0].time - tie[1].time)
        print(
            f'| {tie[1].comment:40} | {tie[1].time:6.1f} | {tie[0].comment:40} | {tie[0].time:6.1f} | {tie[0].time - tie[1].time:6.1f} |'
        )
    # mid_max_min = time_difference_mid_max_min()
    # print(f'Mean (Ta - Tb): {mid_max_min.mid:.2f} ±{mid_max_min.tolerance:.1f} (s)')


def main() -> int:
    print_video_a_video_b_ties()
    print()
    print_video_a_video_b_ties_markdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
