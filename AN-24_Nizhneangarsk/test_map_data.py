

import pytest

import map_data
import map_funcs


@pytest.mark.parametrize(
    'tile_a, point_a, tile_b, expected',
    (
        # Threshold in x/y of tile 3 of other tiles
        (3, map_data.RUNWAY_22_THRESHOLD_TILE_3, 1, map_funcs.Point(-431, 2282)),
        (3, map_data.RUNWAY_22_THRESHOLD_TILE_3, 2, map_funcs.Point(476, 1434)),
        (3, map_data.RUNWAY_22_THRESHOLD_TILE_3, 4, map_funcs.Point(2250, -318)),
        (3, map_data.RUNWAY_22_THRESHOLD_TILE_3, 5, map_funcs.Point(2678, -1052)),
    )
)
def test_point_tile_to_tile(tile_a, point_a, tile_b, expected):
    result = map_funcs.point_tile_to_tile(tile_a, point_a, tile_b)
    assert result == expected


@pytest.mark.parametrize(
    'tile_a, point_a, tile_b, point_b, expected',
    (
        (3, map_data.RUNWAY_22_THRESHOLD_TILE_3, 3, map_data.RUNWAY_22_THRESHOLD_TILE_3, map_funcs.Distance(0, 0)),
        (1, map_funcs.Point(566, 1091), 2, map_funcs.Point(1473, 243), map_funcs.Distance(0, 0)),
        (2, map_funcs.Point(1473, 243), 1, map_funcs.Point(566, 1091), map_funcs.Distance(0, 0)),
        (2, map_funcs.Point(1212, 1202), 3, map_funcs.Point(1508, 350), map_funcs.Distance(0, 0)),
        (3, map_funcs.Point(1508, 350), 2, map_funcs.Point(1212, 1202), map_funcs.Distance(0, 0)),
        (3, map_funcs.Point(419, 990), 4, map_funcs.Point(1897, 90), map_funcs.Distance(0, 0)),
        (4, map_funcs.Point(1897, 90), 3, map_funcs.Point(419, 990), map_funcs.Distance(0, 0)),
        (4, map_funcs.Point(1377, 1107), 5, map_funcs.Point(1805, 373), map_funcs.Distance(0, 0)),
        (5, map_funcs.Point(1805, 373), 4, map_funcs.Point(1377, 1107), map_funcs.Distance(0, 0)),
        # Threshold in x/y of tile 3 of other tiles
        (1, map_funcs.Point(-431, 2282), 3, map_data.RUNWAY_22_THRESHOLD_TILE_3, map_funcs.Distance(0, 0)),
        (2, map_funcs.Point(476, 1434), 3, map_data.RUNWAY_22_THRESHOLD_TILE_3, map_funcs.Distance(0, 0)),
        (4, map_funcs.Point(2250, -318), 3, map_data.RUNWAY_22_THRESHOLD_TILE_3, map_funcs.Distance(0, 0)),
        (5, map_funcs.Point(2678, -1052), 3, map_data.RUNWAY_22_THRESHOLD_TILE_3, map_funcs.Distance(0, 0)),
    )
)
def test_distance_tile_to_tile(tile_a, point_a, tile_b, point_b, expected):
    result = map_funcs.distance_tile_to_tile(tile_a, point_a, tile_b, point_b)
    assert result == expected

