# set logscale x
set colorsequence classic
set grid
set title "Distance from video B."
set xlabel "Video A Time [Video B time + 34.25] (s)"
set xtics
set xrange [35:47]
#set format x ""

# set logscale y
set ylabel "Distance from Runway Start (m)"
#set yrange [:2000]
# set ytics 8,35,3
# set logscale y2
#set y2label "Difference (m)"
#set y2range [-6:3]
#set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "video_b_distance.svg"   # choose the output device
#set key title "Window Length"
set key left top
#  lw 2 pointsize 2

# Start distance arrows and labels
#set arrow from 40,1653 to 55,1653 lt 1 nohead
#set label "Runway end 1653m" at 47.5,1800 center font ",12"

# video_b_distance_from_bearings(t) = 6.072e+02 + 8.230e+01 * t + 7.719e-01 * t**2 + -1.221e-01 * t**3
# video_b_distance_from_tail_height(t) = 3.573e+02 + 2.454e+02 * t + -4.653e+01 * t**2 + 3.802e+00 * t**3
# video_b_distance_from_span(t) = 5.942e+02 + 1.504e+02 * t + -2.753e+01 * t**2 + 3.222e+00 * t**3

#video_b_distance_from_bearings           (t) = 3.600e+03 + -4.003e+02 * t + 1.332e+01 * t**2 + -1.221e-01 * t**3
#video_b_distance_from_tail_height        (t) = -2.154e+05 + 1.681e+04 * t + -4.372e+02 * t**2 + 3.802e+00 * t**3
#video_b_distance_from_span               (t) = -1.663e+05 + 1.337e+04 * t + -3.586e+02 * t**2 + 3.222e+00 * t**3


video_b_distance_from_bearings           (t) = 6.072e+02 + 8.230e+01 * t + 7.719e-01 * t**2 + -1.221e-01 * t**3
video_b_distance_from_tail_height        (t) = 3.573e+02 + 2.454e+02 * t + -4.653e+01 * t**2 + 3.802e+00 * t**3
video_b_distance_from_span               (t) = 5.942e+02 + 1.504e+02 * t + -2.753e+01 * t**2 + 3.222e+00 * t**3

# Criudely copied from tile_distance.plt
slab_distance(t) = -4218.0 + t * (2.843e+02 + t * (-1.645e+01 / 2.0 + t * (4.789e-01 / 3.0 + t * -4.952e-03 / 4.0)))



plot "video_b_bearings.dat" using 1:2:3:4 title "Bearing data" w yerrorbars, \
    "video_b_bearings.dat" using 1:(video_b_distance_from_bearings($1-34.25)) title "Bearings fitted to mid values" lw 2 w line, \
    "video_b_tail_height.dat" using 1:2:3:4 title "Tail height data" w yerrorbars, \
    "video_b_tail_height.dat" using 1:(video_b_distance_from_tail_height($1-34.25)) title "Tail height fitted to mid values" lw 2 w line smooth csplines, \
    "video_b_span.dat" using 1:2:3:4 title "Span data" w yerrorbars, \
    "video_b_span.dat" using 1:(video_b_distance_from_span($1-34.25)) title "Span fitted to mid values" lw 2 w line, \
    "slab_speed_data.dat" using 2:(slab_distance($2)) title "Slab data fitted to mid values" lw 2 w line

# linespoints
#plot "video_b.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "video_b.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "video_b.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
