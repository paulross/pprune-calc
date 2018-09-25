import typing

import numpy as np
from scipy.optimize import curve_fit

from analysis import video_data
from analysis import video_utils


def _pitch(t: float) -> float:
    """Returns the apparent pitch angle of the aircraft at time t.
    Due to camera roll this may not be accurate."""
    xS = [v.video_time.time for v in video_data.AIRCRAFT_PITCHES]
    yS = [v.angle for v in video_data.AIRCRAFT_PITCHES]
    return video_utils.interpolate(xS, yS, t)


def pitch(t: float, min_mid_max: video_data.ErrorDirection) -> float:
    """Returns the apparent pitch angle of the aircraft at time t.
    Due to camera roll this may not be accurate.
    If min_mid_max non zero this applies worst time and measurement error"""
    return video_data.apply_min_mid_max_error(_pitch, t, min_mid_max, video_data.ERROR_PITCH)


def pitches(min_mid_max: video_data.ErrorDirection) -> np.ndarray:
    """Returns a two columns array of time (s) and pitch (degrees) for the
    observed data."""
    data = []
    for pitch in video_data.AIRCRAFT_PITCHES:
        if min_mid_max == video_data.ErrorDirection.MIN:
            data.append(
                (
                    pitch.video_time.time - video_data.ERROR_TIMESTAMP,
                    pitch.angle - video_data.ERROR_PITCH
                )
            )
        elif min_mid_max == video_data.ErrorDirection.MAX:
            data.append(
                (
                    pitch.video_time.time + video_data.ERROR_TIMESTAMP,
                    pitch.angle + video_data.ERROR_PITCH,
                )
            )
        else:
            data.append((pitch.video_time.time, pitch.angle))
    return np.array(data, dtype=np.float64)


def pitch_curve_fit(min_mid_max: video_data.ErrorDirection):
    """Returns the polynomial coefficients of the fit to the pitch data."""
    data = pitches(min_mid_max)
    # Third order polynomial
    popt, _pcov = curve_fit(
        video_utils.polynomial_3,
        data[:, 0],
        data[:, 1],
    )
    return popt


def pitch_fitted_line():
    pitch_fit = pitch_curve_fit(video_data.ErrorDirection.MID)
    start = int(video_data.AIRCRAFT_ASPECTS[0].video_time.time)
    stop = int(0.5 + video_data.AIRCRAFT_ASPECTS[-1].video_time.time)
    temp = []
    for t in range(start, stop + 1, 1):
        bearing = video_utils.polynomial_3(t, *pitch_fit)
        temp.append((t, bearing))
    array = np.asarray(temp)
    return array
