import math

import pytest

from analysis import video_data

@pytest.mark.parametrize(
    'frame, expected',
    (
        (0, video_data.VideoTime(0, 0, 0)),
        (30, video_data.VideoTime(0, 1, 0)),
        (30 * 60, video_data.VideoTime(1, 0, 0)),
    ),
)
def test_video_frame_to_time(frame, expected):
    assert expected == video_data.video_frame_to_time(frame)

VIDEO_TIME_TO_FFMPEG_TIME_DATA = (
    (video_data.VideoTime(0, 0, 0), video_data.VideoTime(0, 0, 2)),
    (video_data.VideoTime(0, 1, 0), video_data.VideoTime(0, 1, 2)),
    (video_data.VideoTime(1, 0, 0), video_data.VideoTime(1, 0, 2)),
)


@pytest.mark.parametrize(
    'video_time, ffmpeg_time',
    VIDEO_TIME_TO_FFMPEG_TIME_DATA,
)
def test_video_time_to_ffmepeg_time(video_time, ffmpeg_time):
    assert ffmpeg_time == video_data.video_time_to_ffmpeg_time(video_time)


@pytest.mark.parametrize(
    'video_time, ffmpeg_time',
    VIDEO_TIME_TO_FFMPEG_TIME_DATA,
)
def test_video_time_to_ffmepeg_time(video_time, ffmpeg_time):
    assert video_time == video_data.ffmpeg_time_to_video_time(ffmpeg_time)


VIDEO_TIME_TO_FFMPEG_NAME_DATA = (
    (video_data.VideoTime(0, 0, 0), 'image000002.png'),
    (video_data.VideoTime(0, 1, 0), 'image000032.png'),
    (video_data.VideoTime(0, 8, 14), 'image000256.png'),
    (video_data.VideoTime(0, 25, 19), 'image000771.png'),
    (video_data.VideoTime(0, 27, 24), 'image000836.png'),
    (video_data.VideoTime(0, 33, 18), 'image001010.png'),
)

@pytest.mark.parametrize(
    'video_time, ffmpeg_name',
    VIDEO_TIME_TO_FFMPEG_NAME_DATA,
)
def test_video_time_to_ffmepeg_name(video_time, ffmpeg_name):
    assert ffmpeg_name == video_data.video_time_to_ffmpeg_name(video_time)


@pytest.mark.parametrize(
    'video_time, ffmpeg_name',
    VIDEO_TIME_TO_FFMPEG_NAME_DATA,
)
def test_ffmepeg_name_to_video_time(video_time, ffmpeg_name):
    assert video_time == video_data.ffmpeg_name_to_video_time(ffmpeg_name)


@pytest.mark.parametrize(
    'video_time, span, length, note, expected',
    (
        (video_data.VideoTime(0, 0, 0), video_data.AIRCRAFT_SPAN, 0.0,                          '', 0),
        (video_data.VideoTime(0, 0, 0), video_data.AIRCRAFT_SPAN, video_data.AIRCRAFT_LENGTH,   '', 45),
        (video_data.VideoTime(0, 0, 0), 0.0, video_data.AIRCRAFT_LENGTH,                        '', 90),
        (video_data.VideoTime(0, 0, 0), -video_data.AIRCRAFT_SPAN, video_data.AIRCRAFT_LENGTH,  '', 135),
        (video_data.VideoTime(0, 0, 0), -video_data.AIRCRAFT_SPAN, 0.0,                         '', 180),
        (video_data.VideoTime(0, 0, 0), -video_data.AIRCRAFT_SPAN, -video_data.AIRCRAFT_LENGTH, '', 225),
        (video_data.VideoTime(0, 0, 0), 0.0, -video_data.AIRCRAFT_LENGTH,                       '', 270),
        (video_data.VideoTime(0, 0, 0), video_data.AIRCRAFT_SPAN, -video_data.AIRCRAFT_LENGTH,  '', 315),
    ),
)
def test_aircraft_aspect_wing_tips_angle(video_time, span, length, note, expected):
    aawt = video_data.AircraftAspectWingTips(video_time, span, length, note)
    assert expected == aawt.angle


@pytest.mark.parametrize(
    'video_time, span, length, note, expected',
    (
        (video_data.VideoTime(0, 0, 0), video_data.AIRCRAFT_SPAN, 0.0,                          '', 21.97),
        (video_data.VideoTime(0, 0, 0), video_data.AIRCRAFT_SPAN, video_data.AIRCRAFT_LENGTH,   '', 16.33),
        (video_data.VideoTime(0, 0, 0), 0.0, video_data.AIRCRAFT_LENGTH,                        '', 22.60),
        (video_data.VideoTime(0, 0, 0), -video_data.AIRCRAFT_SPAN, video_data.AIRCRAFT_LENGTH,  '', 16.33),
        (video_data.VideoTime(0, 0, 0), -video_data.AIRCRAFT_SPAN, 0.0,                         '', 21.97),
        (video_data.VideoTime(0, 0, 0), -video_data.AIRCRAFT_SPAN, -video_data.AIRCRAFT_LENGTH, '', 16.33),
        (video_data.VideoTime(0, 0, 0), 0.0, -video_data.AIRCRAFT_LENGTH,                       '', 22.60),
        (video_data.VideoTime(0, 0, 0), video_data.AIRCRAFT_SPAN, -video_data.AIRCRAFT_LENGTH,  '', 16.33),
    ),
)
def test_aircraft_aspect_wing_tips_error(video_time, span, length, note, expected):
    aawt = video_data.AircraftAspectWingTips(video_time, span, length, note)
    assert math.isclose(expected, aawt.error, rel_tol=0.001)
    # assert expected == aawt.error
