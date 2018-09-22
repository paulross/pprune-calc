import math

from analysis import video_analysis

import pytest
from hypothesis import given
import hypothesis.strategies as hst

@pytest.mark.parametrize(
    'm, k',
    (
        (1, 1.942602569415665),
    ),
)
def test_m_p_s_to_knots(m, k):
    assert k == video_analysis.m_p_s_to_knots(m)


@pytest.mark.parametrize(
    'm, k',
    (
        (1, 1.942602569415665),
    ),
)
def test_knots_to_m_p_s(m, k):
    assert m == video_analysis.knots_to_m_p_s(k)


@given(hst.floats(allow_nan=False, allow_infinity=False, width=32))
def test_knots_to_m_p_s_and_back(k):
    assert math.isclose(k, video_analysis.m_p_s_to_knots(video_analysis.knots_to_m_p_s(k)))


@given(hst.floats(allow_nan=False, allow_infinity=False, width=32))
def test_m_p_s_to_knots_and_back(m):
    assert math.isclose(m, video_analysis.knots_to_m_p_s(video_analysis.m_p_s_to_knots(m)))


@pytest.mark.parametrize(
    'n, k, expected',
    (
        (1, 1, 1),
        (2, 2, 1),
        (10, 10, 1),
        (10, 11, 0),
        (3, 2, 3),
        (52, 5, 2598960), # Poker
        (32, 2, 496),
    ),
)
def test_k_out_of_n(n, k, expected):
    assert expected == video_analysis.num_k_of_n(n, k)


@pytest.mark.parametrize(
    'x, y',
    (
        (4, 8),
        (8, 16),
        (6, 12),
        (2, 4),
        (0, 0),
        (16, 32),
        (18, 36),
        (20, 40),
    ),
)
def test_interpolate(x, y):
    xS = list(range(4, 17, 4))
    yS = [v * 2 for v in xS]
    assert y == video_analysis.interpolate(xS, yS, x)


@pytest.mark.parametrize(
    'd0, b0, d1, b1, expected_d, expected_y',
    (
        (0.0, 45.0, 1.0, 90.0, 1.0, 1.0),
        (0.0, 30.0, math.cos(math.radians(30)), 90.0, math.cos(math.radians(30)), 0.5),
        (10.0, 45.0, 11.0, 90.0, 11.0, 1.0),
        (0.0, 45.0, 1.0, 135.0, 0.5, 0.5),
        # To the left
        (0.0, 315.0, 1.0, 270.0, 1.0, -1.0),
        (0.0, 330.0, math.cos(math.radians(30)), 270.0, math.cos(math.radians(30)), -0.5),
    ),
)
def test_aspect_intersection(d0, b0, d1, b1, expected_d, expected_y):
    d, y = video_analysis.aspect_intersection(d0, b0, d1, b1)
    assert math.isclose(expected_d, d)
    assert math.isclose(expected_y, y)


if __name__ == '__main__':
    pytest.main()
