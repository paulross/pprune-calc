# set logscale x
set colorsequence classic
set grid
set title "Comparison of Ground Speed From Slab Count and Video B Bearings."
set xlabel "Video A Time [Video B time + 34.25] (s)"
set xtics
#set xrange [27:31.5]
set xrange [25:50]
#set format x ""

# set logscale y
set ylabel "Speed (m/s)"
#set yrange [30:100]
# set ytics 8,35,3
# set logscale y2

set y2label "Difference (m/s)"
set y2range [-15:20]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "speed_cmp_slab_video_b.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# arrows and labels
#set arrow from 27.57,70 to 27.57,87 lt 1
#set label "Threshold\nt=27.6s" at 27.57,69 center font ",12"
#set arrow from 33.83,70 to 33.83,82 lt 1
#set label "Touchdown\nt=33.8s" at 33.83,69 center font ",12"


# Differential of d coefficients: -2.481e+03, 8.276e+01, 5.914e-01, -1.173e-02
slab_speed(t) = 2.843e+02 + -1.645e+01 * t + 4.789e-01 * t**2 + -4.952e-03 * t**3
video_b_speed_from_bearings              (t) = 8.230e+01 + 1.544e+00 * t + -3.663e-01 * t**2


plot "slab_speed_data.dat" using 2:3:4:5 title "Video A, Slab data" w yerrorbars, \
    "slab_speed_data.dat" using 2:(slab_speed($2)) title "Video A, fitted to mid" lw 2 w line smooth csplines, \
    "video_b_bearings.dat" using 1:5:6:7 title "Video B, from Bearings" w yerrorbars, \
    "video_b_bearings.dat" using 1:(video_b_speed_from_bearings($1-34.25)) title "Video B, fitted to mid" lw 2 w line smooth csplines, \
    "video_b_bearings.dat" using 1:(video_b_speed_from_bearings($1-34.25) - slab_speed($1)) title "Difference (right)" axes x1y2 lw 2 dt 4 w line smooth csplines

# linespoints
#plot "tile_distance_data.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "tile_distance_data.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "tile_distance_data.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
