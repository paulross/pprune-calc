# set logscale x
set colorsequence classic
set grid
set title "Speed."
set xlabel "Video Time (s)"
set xtics
set xrange [-5:50]
#set format x ""

# set logscale y
set ylabel "Speed (m/s)"
#set yrange [-2500:1500]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "speed.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# arrows and labels
set arrow from 27.57,70 to 27.57,87 lt 1
set label "Threshold\nt=27.6s" at 27.57,69 center font ",12"
set arrow from 33.83,70 to 33.83,82 lt 1
set label "Touchdown\nt=33.8s" at 33.83,69 center font ",12"


# Differential of d coefficients: -2.481e+03, 8.276e+01, 5.914e-01, -1.173e-02
tile_speed(t) = 8.276e+01 + 5.914e-01 * t * 2.0 + -1.173e-02 * t**2 * 3.0
slab_speed(t) = 2.843e+02 + -1.645e+01 * t + 4.789e-01 * t**2 + -4.952e-03 * t**3
#slab_speed_plus(t) = 5.831e+02 + -3.996e+01 * t + 1.089e+00 * t**2 + -1.015e-02 * t**3


plot "tile_distance_data.dat" using 2:6:7:8 title "Aerial data" w yerrorbars, \
    "tile_distance_data.dat" using 2:(tile_speed($2)) title "Fitted to mid values" lw 2 w line smooth csplines, \
    "slab_speed_data.dat" using 2:3:4:5 title "Slab data" w yerrorbars, \
    "slab_speed_data.dat" using 2:(slab_speed($2)) title "Fitted to mid values" lw 2 w line smooth csplines

# linespoints
#plot "tile_distance_data.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "tile_distance_data.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "tile_distance_data.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
