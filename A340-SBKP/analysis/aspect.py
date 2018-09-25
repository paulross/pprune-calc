import math
import typing

import numpy as np
from scipy.optimize import curve_fit

from analysis import video_data
from analysis import video_utils


def _aspects_curve_fit(data: np.ndarray) -> typing.List[float]:
    """Returns the polynomial coefficients of the fit to the aspects data."""
    # Third order polynomial
    popt, _pcov = curve_fit(
        video_utils.polynomial_3,
        data[:, 0],
        data[:, 1],
    )
    return popt


def aspect_from_fit(t: float, fit: typing.List[float]) -> float:
    """Returns the aspect for time t and fit."""
    return video_utils.polynomial_3(t, *fit)


def _aspect_fitted_line(fit: typing.List[float], start: int, stop: int) -> np.ndarray:
    temp = []
    for t in range(start, stop + 1, 1):
        bearing = video_utils.polynomial_3(t, *fit)
        temp.append((t, bearing))
    array = np.asarray(temp)
    return array


def _aspects(
        input_data: typing.Sequence[typing.Union[video_data.AircraftAspect, video_data.AircraftAspectWingTips]],
        min_mid_max: video_data.ErrorDirection) -> np.ndarray:
    """Returns a two columns array of time (s) and aspect (degrees) for the
    observed data."""
    temp  =[]
    for aspect in input_data:
        if min_mid_max == video_data.ErrorDirection.MIN:
            temp.append(
                (
                    aspect.video_time.time - video_data.ERROR_TIMESTAMP,
                    aspect.angle - aspect.error
                )
            )
        elif min_mid_max == video_data.ErrorDirection.MAX:
            temp.append(
                (
                    aspect.video_time.time + video_data.ERROR_TIMESTAMP,
                    aspect.angle + aspect.error,
                )
            )
        else:
            temp.append((aspect.video_time.time, aspect.angle))
    return np.array(temp, dtype=np.float64)


def aspects(min_mid_max: video_data.ErrorDirection) -> np.ndarray:
    return _aspects(video_data.AIRCRAFT_ASPECTS, min_mid_max)

def aspects_curve_fit(min_mid_max: video_data.ErrorDirection):
    data = aspects(min_mid_max)
    return _aspects_curve_fit(data)


ASPECT_FIT = {
    k : aspects_curve_fit(k) for k in list(video_data.ErrorDirection)
}


def aspect_fitted_line() -> np.ndarray:
    aspects_fit = aspects_curve_fit(video_data.ErrorDirection.MID)
    start = int(video_data.AIRCRAFT_ASPECTS[0].video_time.time)
    stop = int(0.5 + video_data.AIRCRAFT_ASPECTS[-1].video_time.time)
    return _aspect_fitted_line(aspects_fit, start, stop)


def aspects_from_wing_tips(min_mid_max: video_data.ErrorDirection) -> np.ndarray:
    """Returns a two columns array of time (s) and aspect (degrees) for the
    observed data."""
    return _aspects(video_data.AIRCRAFT_ASPECTS_FROM_WING_TIPS, min_mid_max)


def aspects_curve_fit_from_wing_tips(min_mid_max: video_data.ErrorDirection):
    return _aspects_curve_fit(aspects_from_wing_tips(min_mid_max))


ASPECT_FIT_FROM_WING_TIPS = {
    k : aspects_curve_fit_from_wing_tips(k) for k in list(video_data.ErrorDirection)
}


def aspect_from_wing_tips_fitted_line() -> np.ndarray:
    aspects_fit = aspects_curve_fit_from_wing_tips(video_data.ErrorDirection.MID)
    start = int(video_data.AIRCRAFT_ASPECTS_FROM_WING_TIPS[0].video_time.time)
    stop = int(0.5 + video_data.AIRCRAFT_ASPECTS_FROM_WING_TIPS[-1].video_time.time)
    return _aspect_fitted_line(aspects_fit, start, stop)


