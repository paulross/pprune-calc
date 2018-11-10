"""
Plots video data.
"""
import shutil
import sys


from analysis import plot_acceleration, plot_angle_of_view
from analysis import plot_aspect
from analysis import plot_common
from analysis import plot_constants
from analysis import plot_distance
from analysis import plot_events
from analysis import plot_ground_speed
from analysis import plot_observer
from analysis import plot_pitch
from analysis import plot_svg
from analysis import plot_transits
from analysis import plot_yaw


def main():
    if shutil.which('gnuplot') is None:
        print('ERROR: gnuplot is not installed or not on the PATH')
        return -1

    plot_common.write_dat_plt_call(
        'ground_speed',
        plot_ground_speed.gnuplot_ground_speed,
        plot_ground_speed.gnuplot_ground_speed_plt,
    )
    plot_common.write_dat_plt_call(
        'ground_speed_extrapolated',
        plot_ground_speed.gnuplot_ground_speed_extrapolated,
        plot_ground_speed.gnuplot_ground_speed_extrapolated_plt,
    )
    plot_common.write_dat_plt_call(
        'acceleration',
        plot_acceleration.gnuplot_acceleration,
        plot_acceleration.gnuplot_acceleration_plt,
    )
    plot_common.write_dat_plt_call(
        'distance',
        plot_distance.gnuplot_distance,
        plot_distance.gnuplot_distance_plt,
    )
    plot_common.write_dat_plt_call(
        'distance_runway_end',
        plot_distance.gnuplot_distance_runway_end,
        plot_distance.gnuplot_distance_runway_end_plt
    )
    plot_common.write_dat_plt_call(
        'distance_from_transits',
        plot_distance.gnuplot_distance_from_transits,
        plot_distance.gnuplot_distance_from_transits_plt,
    )
    plot_common.write_dat_plt_call(
        'pitch',
        plot_pitch.gnuplot_pitch,
        plot_pitch.gnuplot_pitch_plt,
    )
    plot_common.write_dat_plt_call(
        'aspect',
        plot_aspect.gnuplot_aspect,
        plot_aspect.gnuplot_aspect_plt,
    )
    plot_common.write_dat_plt_call(
        'time_distance_bearing',
        plot_observer.gnuplot_observer_time_distance_bearing,
        plot_observer.gnuplot_observer_time_distance_bearing_plt,
    )
    plot_common.write_dat_plt_call(
        'observer_xy',
        plot_observer.gnuplot_observer_xy,
        plot_observer.gnuplot_observer_xy_plt,
    )
    # FIXME:
    plot_common.write_dat_plt_call(
        'time_distance_bearing_with_yaw',
        plot_observer.gnuplot_observer_time_distance_bearing_with_yaw,
        plot_observer.gnuplot_observer_time_distance_bearing_plt,
    )
    plot_common.write_dat_plt_call(
        'aircraft_yaw',
        plot_yaw.gnuplot_aircraft_yaw,
        plot_yaw.gnuplot_aircraft_yaw_plt,
    )
    plot_common.write_dat_plt_call(
        'ground_transits',
        plot_transits.gnuplot_ground_transits,
        plot_transits.gnuplot_ground_transits_plt,
    )
    plot_common.write_dat_plt_call(
        'full_transits',
        plot_transits.gnuplot_full_transits,
        plot_transits.gnuplot_full_transits_plt,
    )
    plot_common.write_dat_plt_call(
        'angle_of_view',
        plot_angle_of_view.gnuplot_angle_of_view,
        plot_angle_of_view.gnuplot_angle_of_view_plt,
    )

    # print('\n'.join(create_svg()))

    plot_svg.modify_svg_as_text_and_copy(
        plot_constants.OSM_SVG_FILENAME,
        '../plots/OpenStreetmap_SBKP_01_annotated.svg',
    )

    for v in plot_events.gen_event_data():
        print(v)

    # table = create_event_table()
    # pprint.pprint(table, width=180)
    plot_events.print_event_table_markdown()

    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
