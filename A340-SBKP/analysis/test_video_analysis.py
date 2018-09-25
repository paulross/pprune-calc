import pytest

from analysis import video_data
from analysis import video_analysis


@pytest.mark.parametrize(
    't, dt, min_mid_max, expected',
    (
        (0.0, 1.0, video_data.ErrorDirection.MIN, 56.81304372873357),
        (0.0, 1.0, video_data.ErrorDirection.MID, 63.518551116914246),
        (0.0, 1.0, video_data.ErrorDirection.MAX, 69.58038559428908),
    ),
)
def test_ground_sped_raw(t, dt, min_mid_max, expected):
    gs = video_analysis.ground_speed_raw(t, dt, min_mid_max)
    assert expected == gs



if __name__ == '__main__':
    pytest.main()
