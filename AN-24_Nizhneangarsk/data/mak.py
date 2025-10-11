"""
Data from the MAK preliminary report.
"""

# Data from the radar plot of image 3
import datetime
import math
import pprint
import sys

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
    IMAGE_3_RAW_PLOTS_TIME_START + datetime.timedelta(seconds=i * IMAGE_3_RAW_PLOTS_TIME_INTERVAL_SECONDS): (b, r * 1e-3 * IMAGE_3_SCALE)
    for i, (b, r) in enumerate(IMAGE_3_RAW_PLOTS)
}

IMAGE_3_COMPUTED_X_Y = {
    k: (
        r * math.cos(math.radians(b)),
        r * math.sin(math.radians(b)),
    )
    for k, (b, r) in IMAGE_3_COMPUTED_BEARING_RANGE.items()
}


def main():
    # print(IMAGE_3_SCALE)
    # pprint.pprint(IMAGE_3_COMPUTED_X_Y)

    keys = sorted(IMAGE_3_COMPUTED_X_Y.keys())
    for i in range(1, len(keys)):
        dx = IMAGE_3_COMPUTED_X_Y[keys[i]][0] - IMAGE_3_COMPUTED_X_Y[keys[i-1]][0]
        dy = IMAGE_3_COMPUTED_X_Y[keys[i]][1] - IMAGE_3_COMPUTED_X_Y[keys[i-1]][1]
        dd = math.sqrt(dx**2 + dy**2)
        print(
            f'{i:4d} {keys[i]}'
            f' {IMAGE_3_COMPUTED_BEARING_RANGE[keys[i]][0]:8.1f} {IMAGE_3_COMPUTED_BEARING_RANGE[keys[i]][1]:8.1f}'
            f' {dd:8.1f} {dd / 30:8.1f} {dd * 3600 / 30 / 1852:8.1f}'
        )
    return 0


if __name__ == '__main__':
    sys.exit(main())

