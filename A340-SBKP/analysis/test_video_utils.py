import math

import pytest
from hypothesis import given
import hypothesis.strategies as hst

from analysis import video_utils


@pytest.mark.parametrize(
    'm, k',
    (
        (1, 1.942602569415665),
        (5, 9.713012847078325),
    ),
)
def test_m_p_s_to_knots(m, k):
    assert k == video_utils.m_p_s_to_knots(m)


@pytest.mark.parametrize(
    'm, k',
    (
        (1, 1.942602569415665),
    ),
)
def test_knots_to_m_p_s(m, k):
    assert m == video_utils.knots_to_m_p_s(k)


@given(hst.floats(allow_nan=False, allow_infinity=False, width=32))
def test_knots_to_m_p_s_and_back(k):
    assert math.isclose(k, video_utils.m_p_s_to_knots(video_utils.knots_to_m_p_s(k)))


@given(hst.floats(allow_nan=False, allow_infinity=False, width=32))
def test_m_p_s_to_knots_and_back(m):
    assert math.isclose(m, video_utils.knots_to_m_p_s(video_utils.m_p_s_to_knots(m)))


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
    assert expected == video_utils.num_k_of_n(n, k)


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
    # [4, 8, 12, 16]
    xS = list(range(4, 17, 4))
    # [8, 16, 24, 32]
    yS = [v * 2 for v in xS]
    assert y == video_utils.interpolate(xS, yS, x)


@pytest.mark.parametrize(
    'x0, y0, x1, y1, proportion, expected',
    (
        (0, 0, 8, 8, 1 / 2.0, (4, 4)),
    ),
)
def test_interpolate_between_two_points(x0, y0, x1, y1, proportion, expected):
    assert expected == video_utils.interpolate_between_two_points(x0, y0, x1, y1, proportion)


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
    d, y = video_utils.aspect_intersection(d0, b0, d1, b1)
    assert math.isclose(expected_d, d)
    assert math.isclose(expected_y, y)


@pytest.mark.parametrize(
    'x00, y00, x01, y01, x10, y10, x11, y11, expected',
    (
        (
            0, 0, 1, 1,
            0, 1, 1, 1,
            (1, 1),
        ),
        (
            0, 0, 2, 2,
            8, 0, 6, 2,
            (4, 4),
        ),
        # # Full transit from Tower 8              to Concrete block hut  : (125.279980944823, 707.8758276857575) (2146.0969961863984, -231.2907541223004)
        # # Full transit from Trees right of Fedex to Factory interior corner: (2452.9657502621976, 384.50753297703915) (3178.040481477931, -356.6795624918748)
        # # Full transit from Tall radio tower     to Building corner     : (3032.1063544106087, 814.9559001880468) (3274.3474416526055, -140.67283110970288)
        #
        # # Full transit from Tower 8              to Concrete block hut  : (125.279980944823, 707.8758276857575) (2146.0969961863984, -231.2907541223004)
        # # Full transit from Trees right of Fedex to Factory interior corner: (2729.62631272838, 383.37932910566354) (3178.040481477931, -356.6795624918748)
        # # Full transit from Tall radio tower     to Building corner     : (3032.1063544106087, 814.9559001880468) (3274.3474416526055, -140.67283110970288)
        # (
        #     # Tower 8 to Concrete block hut
        #     125.279980944823, 707.8758276857575, 2146.0969961863984, -231.2907541223004,
        #     # Trees right of Fedex to Factory interior corner
        #     2729.62631272838, 383.37932910566354, 3178.040481477931, -356.6795624918748,
        #     # Expected
        #     (3476.7830633005156, -849.7217529140319),
        # ),
        # (
        #     # Trees right of Fedex to Factory interior corner
        #     2729.62631272838, 383.37932910566354, 3178.040481477931, -356.6795624918748,
        #     # Tall radio tower to Building corner
        #     3032.1063544106087, 814.9559001880468, 3274.3474416526055, -140.67283110970288,
        #     # Expected
        #     (3437.7562464087064, -785.3122296108911),
        # ),
        # (
        #     # Tower 8 to Concrete block hut
        #     125.279980944823, 707.8758276857575, 2146.0969961863984, -231.2907541223004,
        #     # Tall radio tower to Building corner
        #     3032.1063544106087, 814.9559001880468, 3274.3474416526055, -140.67283110970288,
        #     # Expected
        #     (3451.05201306389, -837.763350785191),
        # ),
    ),
)
def test_intersect_two_lines(x00, y00, x01, y01, x10, y10, x11, y11, expected):
    result = video_utils.intersect_two_lines(x00, y00, x01, y01, x10, y10, x11, y11)
    # print('XXXX', result)
    assert expected == result


@pytest.mark.parametrize(
    'note_url, exp_note, exp_lat, exp_lon',
    (
        (
            'Tower 1: https://www.google.com/maps/@-23.0039523,-47.1506005,59m/data=!3m1!1e3?hl=en',
            'Tower 1', -23.0039523, -47.1506005,
        ),
        (
            'Tower 2: https://www.google.com/maps/@-23.004224,-47.1502493,59m/data=!3m1!1e3?hl=en',
            'Tower 2', -23.004224, -47.1502493,
        ),
        (
            'Tower 3: https://www.google.com/maps/@-23.0044624,-47.1498953,59m/data=!3m1!1e3?hl=en',
            'Tower 3', -23.0044624, -47.1498953,
        ),
        (
            'Tower 4: https://www.google.com/maps/@-23.0047257,-47.1495659,59m/data=!3m1!1e3?hl=en',
            'Tower 4', -23.0047257, -47.1495659,
        ),
        (
            'Tower 5: https://www.google.com/maps/@-23.00498,-47.1492158,59m/data=!3m1!1e3?hl=en',
            'Tower 5', -23.00498, -47.1492158,
        ),
        (
            'Tower 6: https://www.google.com/maps/@-23.0052343,-47.148865,59m/data=!3m1!1e3?hl=en',
            'Tower 6', -23.0052343, -47.148865,
        ),
    )
)
def test_google_earth_url_to_lat_long(note_url, exp_note, exp_lat, exp_lon):
    note, lat, lon = video_utils.google_earth_url_to_lat_long(note_url)
    assert exp_note == note
    assert exp_lat == lat, 'Difference = {}'.format(lat - exp_lat)
    assert exp_lon == lon, 'Difference = {}'.format(lon - exp_lon)


@pytest.mark.parametrize(
    'lat1, lon1, lat2, lon2, expected_distance',
    (
        (
            # Threshold 15 to end asphalt 15
            # Was, with haversine calculation
            # -22.9985032, -47.1469772, -23.0163963, -47.1219874, 3244.0671201910636,
            # Now with utm.from_latlon()
            -22.9985032, -47.1469772, -23.0163963, -47.1219874, 3239.411931984478,
        ),
        (
            # Threshold 15 to threshold 33
            # Was, with haversine calculation
            # -22.9985032, -47.1469772, -23.015869,-47.1227499, 3146.3625099306523,
            # Now with utm.from_latlon()
            -22.9985032, -47.1469772, -23.015869,-47.1227499, 3141.8391266639856,
        ),
    )
)
def test_distance_lat_long(lat1, lon1, lat2, lon2, expected_distance):
    distance = video_utils.distance_lat_long(lat1, lon1, lat2, lon2)
    assert expected_distance == distance, 'Difference = {}'.format(distance - expected_distance)


@pytest.mark.parametrize(
    'lat1, lon1, lat2, lon2, expected_bearing',
    (
        (
            -22.0, -48.0, -21.999999, -48.0, 0.0,
        ),
        (
            -22.0, -48.0, -22.0, -47.999999, 90.0,
        ),
        (
            -22.0, -48.0, -22.000001, -48.0, 180.0,
        ),
        (
            -22.0, -48.0, -22.0, -48.000001, 270.0,
        ),
        (
            # Threshold 15 to end asphalt 15
            -22.9985032, -47.1469772, -23.0163963, -47.1219874, 127.8840333720462,
        ),
        (
            # Threshold 15 to threshold 33
            -22.9985032, -47.1469772, -23.015869,-47.1227499, 127.91369057493286,
        ),
    )
)
def test_bearing_lat_long(lat1, lon1, lat2, lon2, expected_bearing):
    distance = video_utils.bearing_lat_long(lat1, lon1, lat2, lon2)
    assert math.isclose(expected_bearing, distance, abs_tol=1e-6), 'Difference = {}'.format(distance - expected_bearing)


@pytest.mark.parametrize(
    'lat, lon, exp_lat, exp_lon',
    (
        (
            # Threshold 15 to end asphalt 15
            # Was, with haversine calculation
            # -22.9985032, -47.1469772, -23.0163963, -47.1219874
            # Now with utm.from_latlon()
            -22.9985032, -47.1469772, -23.0163963, -47.15035676360211
        ),
        (
            # Threshold 15 to threshold 33
            # Was, with haversine calculation
            # -22.9985032, -47.1469772, -23.015869, -47.1227499,
            # Now with utm.from_latlon()
            -22.9985032, -47.1469772, -23.015869, -47.0171370558709,
        ),
    )
)
def test_lat_long_bearing_distance_to_lat_long(lat, lon, exp_lat, exp_lon):
    distance = video_utils.distance_lat_long(lat, lon, exp_lat, exp_lon)
    bearing = video_utils.bearing_lat_long(lat, lon, exp_lat, exp_lon)
    act_lat, act_lon = video_utils.lat_long_bearing_distance_to_lat_long(lat, lon, distance, bearing)
    assert exp_lon == act_lon, '{} != {}'.format(exp_lon, act_lon)
    # assert exp_lat == act_lat
    # assert (exp_lat, exp_lon) == (act_lat, act_lon), str((act_lat, act_lon))


@pytest.mark.parametrize(
    'latx, lonx, bearing_x, lat, lon, exp_x, exp_y',
    (
        (
            # Threshold 15 to end asphalt 15
            # Was, with haversine calculation
            # -22.9985032, -47.1469772, 127.8840333720462, -23.0163963, -47.1219874, 3244.0671201910636, 0.0,
            # Now with utm.from_latlon()
            -22.9985032, -47.1469772, 127.8840333720462, -23.0163963, -47.1219874, 3239.411931984478, 0.0,
        ),
        (
            # Threshold 15 to threshold 33
            # Was, with haversine calculation
            # -22.9985032, -47.1469772, 127.91369057493286, -23.015869,-47.1227499, 3146.3625099306523, 0.0,
            # Now with utm.from_latlon()
            -22.9985032, -47.1469772, 127.91369057493286, -23.015869,-47.1227499, 3141.8391266639856, 0.0,
        ),
    )
)
def test_lat_long_to_xy(latx, lonx, bearing_x, lat, lon, exp_x, exp_y):
    x, y = video_utils.lat_long_to_xy(latx, lonx, bearing_x, lat, lon)
    assert math.isclose(x, exp_x, abs_tol=1e-6), 'Difference = {}'.format(x - exp_x)
    assert math.isclose(y, exp_y, abs_tol=1e-6), 'Difference = {}'.format(y - exp_y)


@pytest.mark.xfail(reason='FIXME', strict=True)
def test_xy_to_lat_long():
    # FIXME
    assert 0


@pytest.mark.parametrize(
    'px, py, ox, oy, expected',
    (
        (
            2.0, 1.0, 8.0, -2.0, 4.0,
        ),
        (
            6.0, -1.0, 8.0, -2.0, 4.0,
        ),
    )
)
def test_transit_x_axis_intercept(px, py, ox, oy, expected):
    # print(px, py, ox, oy, expected)
    result = video_utils.transit_x_axis_intercept(px, py, ox, oy)
    assert expected == result


@pytest.mark.parametrize(
    'px, py, ox, oy, expected',
    (
        (
            2.0, 1.0, 8.0, -2.0, math.degrees(math.atan2(-3.0, 6.0)),
        ),
    )
)
def test_transit_bearing(px, py, ox, oy, expected):
    result = video_utils.transit_bearing(px, py, ox, oy)
    assert expected == result


@pytest.mark.parametrize(
    'px, py, ox, oy, expected',
    (
        (
            2.0, 1.0, 8.0, -2.0, math.sqrt(36 + 9),
        ),
    )
)
def test_transit_distance(px, py, ox, oy, expected):
    result = video_utils.transit_distance(px, py, ox, oy)
    assert expected == result


@pytest.mark.parametrize(
    'px, py, ox, oy, expected',
    (
        (
            2.0, 1.0, 8.0, -2.0, math.sqrt(36 + 9) / 3.0,
        ),
    )
)
def test_transit_distance_to_x(px, py, ox, oy, expected):
    result = video_utils.transit_distance_to_x(px, py, ox, oy)
    assert expected == result


@pytest.mark.parametrize(
    'px, py, ox, oy, p_err, o_err, expected',
    (
        (
            2.0, 1.0, 8.0, -2.0, 0.6, 0.3, 0.5,
        ),
    )
)
def test_transit_distance_to_x(px, py, ox, oy, p_err, o_err, expected):
    result = video_utils.transit_x_axis_error(px, py, ox, oy, p_err, o_err)
    assert expected == result


if __name__ == '__main__':
    pytest.main()
