# set logscale x
set colorsequence classic
set grid
set title "Acceleration."
set xlabel "Video Time (s)"
set xtics
set xrange [26:]
#set format x ""

# set logscale y
set ylabel "Acceleration (m/s^2)"
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

set output "acceleration.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# arrows and labels
set arrow from 27.57,-3 to 27.57,-2 lt 2
set label "Threshold\nt=27.6s" at 27.57,-3.1 center font ",12"
set arrow from 33.83,-3 to 33.83,-2 lt 2
set label "Touchdown\nt=33.8s" at 33.83,-3.1 center font ",12"

# Differential of v coefficients: 2.843e+02, -1.645e+01, 4.789e-01, -4.952e-03
slab_acceleration(t) = -1.645e+01 + 4.789e-01 * t * 2 + -4.952e-03 * t**2 * 3.0

plot "slab_speed_data.dat" using 2:9:10:11 title "Acceleration" w yerrorbars, \
    "slab_speed_data.dat" using 2:(slab_acceleration($2)) title "Fitted to mid values" lw 2 w line# smooth csplines

reset
