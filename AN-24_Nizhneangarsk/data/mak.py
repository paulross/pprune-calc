"""
Data from the MAK preliminary report.
"""

# Data from the radar plot of image 3
import datetime
import math
import sys

import numpy as np

IMAGE_3_SCALE = 20e3 / 143.0e-3

IMAGE_3_RAW_PLOTS_TIME_START = datetime.datetime(2019, 6, 27, 2, 14, 30)
IMAGE_3_RAW_PLOTS_TIME_INTERVAL_SECONDS = 30

# This is pairs of bearing in degrees and distance in millimetres
IMAGE_3_RAW_PLOTS = (
    (194.0, 91.5),  # 02:14:30 UTC
    (194.0, 71.0),  # 02:15 UTC
    (197.0, 52.0),
    (198.0, 33.0),  # 02:16 UTC
    (180.0, 18.0),
    (124.0, 21.0),  # 02:17 UTC
    (97.0, 36.5),
    (88.0, 55.0),  # 02:18 UTC
    (83.0, 72.0),
    (83.0, 89.0),  # 02:19 UTC
    (84.0, 108.0),
    (80.0, 124.0),  # 02:20 UTC
    (74.0, 135.0),
    (67.0, 135.0),  # 02:21 UTC
    (59.0, 122.5),
    (54.0, 104.0),  # 02:22 UTC
    (51.0, 82.0),
    (46.0, 58.5),  # 02:23 UTC
    (37.0, 38.5),
    (39.0, 17.0),  # 02:24 UTC
    (217.0, 3.5),
)

IMAGE_3_COMPUTED_BEARING_RANGE = {
    IMAGE_3_RAW_PLOTS_TIME_START + datetime.timedelta(seconds=i * IMAGE_3_RAW_PLOTS_TIME_INTERVAL_SECONDS): (
    b, r * 1e-3 * IMAGE_3_SCALE)
    for i, (b, r) in enumerate(IMAGE_3_RAW_PLOTS)
}

IMAGE_3_COMPUTED_X_Y = {
    k: (
        r * math.cos(math.radians(b)),
        r * math.sin(math.radians(b)),
    )
    for k, (b, r) in IMAGE_3_COMPUTED_BEARING_RANGE.items()
}

# Final report
# +/- 0.5 mm
FIGURE_MEASURING_ERROR = 1 / 2

FIGURE_45_SCALE_M_MM = 45.45
FIGURE_45_TIME_DISTANCE = {
    -29.3: -2909.09090909091,
    -22.3: -2204.54545454545,
    -9.3: -931.818181818182,
    -8.3: -818.181818181818,
    -7.3: -704.545454545455,
    -4.8: -454.545454545455,
    -2.0: -227.272727272727,
}
FIGURE_45_DISTANCE_ERROR = FIGURE_MEASURING_ERROR * FIGURE_45_SCALE_M_MM

FIGURE_48_SCALE_M_MM = 9.83
FIGURE_48_TIME_DISTANCE = {
    -8.3: -580.056179775281,
    -7.3: -511.23595505618,
    -4.8: -329.35393258427,
    -2.0: -147.47191011236,
    0: 0,
    0.7: 63.9044943820225,
    4.2: 373.595505617978,
    5.4: 471.910112359551,
    6.2: 535.814606741573,
    7.4: 634.129213483146,
    7.8: 658.707865168539,
    8.4: 707.865168539326,
    10.2: 865.168539325843,
    12.3: 1002.80898876404,
    12.9: 1047.05056179775,
    13.7: 1106.0393258427,
    14.8: 1184.69101123595,
    16.5: 1302.66853932584,
    18.2: 1400.98314606742,
    19.6: 1494.38202247191,
    20.9: 1563.20224719101,
    22.7: 1661.51685393258,
    28.3: 1892.55617977528,
}
FIGURE_48_DISTANCE_ERROR = FIGURE_MEASURING_ERROR * FIGURE_48_SCALE_M_MM

FIGURE_48_TIME_DISTANCE_SORTED_TIMES = sorted(FIGURE_48_TIME_DISTANCE.keys())
FIGURE_48_TIME_DISTANCE_SORTED_DISTANCES = []
for t in FIGURE_48_TIME_DISTANCE_SORTED_TIMES:
    FIGURE_48_TIME_DISTANCE_SORTED_DISTANCES.append(FIGURE_48_TIME_DISTANCE[t])


def interpolate_figure_48(t: float) -> float:
    return np.interp([t,], FIGURE_48_TIME_DISTANCE_SORTED_TIMES, FIGURE_48_TIME_DISTANCE_SORTED_DISTANCES)[0]


# 	Figure 48	My estimate		Difference (m)
# Touchdown	535.8	549		-13.2
# Boundary Fence	1844.2	1853		-8.8
# Final Impact	1898.3	1889		9.3


def main():
    # print(IMAGE_3_SCALE)
    # pprint.pprint(IMAGE_3_COMPUTED_X_Y)

    keys = sorted(IMAGE_3_COMPUTED_X_Y.keys())
    for i in range(1, len(keys)):
        dx = IMAGE_3_COMPUTED_X_Y[keys[i]][0] - IMAGE_3_COMPUTED_X_Y[keys[i - 1]][0]
        dy = IMAGE_3_COMPUTED_X_Y[keys[i]][1] - IMAGE_3_COMPUTED_X_Y[keys[i - 1]][1]
        dd = math.sqrt(dx ** 2 + dy ** 2)
        print(
            f'{i:4d} {keys[i]}'
            f' {IMAGE_3_COMPUTED_BEARING_RANGE[keys[i]][0]:8.1f} {IMAGE_3_COMPUTED_BEARING_RANGE[keys[i]][1]:8.1f}'
            f' {dd:8.1f} {dd / 30:8.1f} {dd * 3600 / 30 / 1852:8.1f}'
        )
    return 0


if __name__ == '__main__':
    sys.exit(main())
