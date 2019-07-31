import sys

import map_funcs

GOOGLE_EARTH_AIRPORT_IMAGES = {
    'GoogleEarth_AirportCamera_C.jpg' : {
        'path': 'video_images/GoogleEarth_AirportCamera_C.jpg',
        'width': 4800,
        'height': 3011,
        # Originally measured on the 100m legend as 181 px
        # 'm_per_px': 100 / (4786 - 4605),
        # Corrected to 185 to give runway length of 1650.5 m
        'm_per_px': 100 / (4786 - 4601),
        'datum': 'runway_22_start',
        'measurements': {
            # 'datum_1': 'runway_22_end',
            'runway_22_start': map_funcs.Point(3217, 204),
            'runway_22_end': map_funcs.Point((1310 + 1356) / 2, (2589 + 2625) / 2),
            'perimeter_fence': map_funcs.Point(967, 2788),
            'red_building': map_funcs.Point(914, 2827),
            'helicopter': map_funcs.Point(2630, 1236),
            'camera_A': map_funcs.Point(2890, 1103),
        }
    },
}


def main() -> int:
    # Check scale and runway length
    print('GoogleEarth_AirportCamera_C.jpg scale',
          GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'])
    print('GoogleEarth_AirportCamera_C.jpg runway length',
          map_funcs.distance(
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_end'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
          ),
          RUNWAY_LENGTH_HEADING[0],
          )
    print('GoogleEarth_AirportCamera_C.jpg runway heading',
          map_funcs.bearing(
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_end'],
          ),
          RUNWAY_LENGTH_HEADING[1],
          )
    print('GoogleEarth_AirportCamera_C.jpg perimeter_fence',
          map_funcs.distance(
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['perimeter_fence'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
          ),
          )
    print('GoogleEarth_AirportCamera_C.jpg red_building',
          map_funcs.distance(
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['runway_22_start'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements']['red_building'],
              GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px'],
          ),
          )

    datum_name = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['datum']
    pt = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'][k]
    origin = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'][datum_name]
    m_per_px = GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['m_per_px']
    new_pt = map_funcs.translate_rotate(pt, 218.09715488381195, origin)
    for k in GOOGLE_EARTH_AIRPORT_IMAGES['GoogleEarth_AirportCamera_C.jpg']['measurements'].keys():
        # print('Rotated', k, new_pt, new_pt.x * m_per_px, new_pt.y * m_per_px)
        print(
            f'Rotated: {k:20}'
            f' Old {pt.x:8.1f} {pt.y:8.1f}'
            f' New {new_pt.x:8.1f} {new_pt.y:8.1f}'
            f' In m {m_per_px * new_pt.x:8.1f} {m_per_px * new_pt.y:8.1f}'
        )

    return 0


if __name__ == '__main__':
    sys.exit(main())