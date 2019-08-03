"""
This is for data that links video A and video B together.
"""
import sys
import typing

import map_funcs
from common import structs
from data import video_a, video_b


FRAME_TIE_DICT: typing.Dict[int, int] = {

}

def create_time_ties() -> typing.List[typing.Tuple[structs.TimeComment, structs.TimeComment]]:
    ret = []
    for frame_a in sorted(FRAME_TIE_DICT.keys()):
        t_a = map_funcs.frame_to_time(frame_a, video_a.FRAME_RATE)
        t_b = map_funcs.frame_to_time(FRAME_TIE_DICT[frame_a], video_b.FRAME_RATE)
        msg_a = video_a.FRAME_EVENTS[frame_a]
        msg_b = video_b.FRAME_EVENTS[FRAME_TIE_DICT[frame_a]]
        ret.append((structs.TimeComment(t_a, msg_a), structs.TimeComment(t_b, msg_b)))
    return ret


def main() -> int:
    return 0


if __name__ == '__main__':
    sys.exit(main())
