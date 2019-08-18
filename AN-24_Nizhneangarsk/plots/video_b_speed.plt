# set logscale x
set colorsequence classic
set grid
set title "Speed from video B."
set xlabel "Video A Time [Video B time + 34.25] (s)"
set xtics
set xrange [35:47]
#set format x ""

# set logscale y
set ylabel "Speed (m/s)"
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

set output "video_b_speed.svg"   # choose the output device
#set key title "Window Length"
# set key left top
#  lw 2 pointsize 2

# Start distance arrows and labels
#set arrow from 40,1653 to 55,1653 lt 1 nohead
#set label "Runway end 1653m" at 47.5,1800 center font ",12"

# d coefficients: -2.481e+03, 8.276e+01, 5.914e-01, -1.173e-02
#tile_distance(t) = -2.481e+03 + 8.276e+01 * t + 5.914e-01 * t**2 + -1.173e-02 * t**3
# Integral of v coefficients: 2.843e+02, -1.645e+01, 4.789e-01, -4.952e-03
# With offset of 4217.960402389347
#slab_distance(t) = -4218.0 + t * (2.843e+02 + t * (-1.645e+01 / 2.0 + t * (4.789e-01 / 3.0 + t * -4.952e-03 / 4.0)))

video_b_speed_from_bearings              (t) = 8.230e+01 + 1.544e+00 * t + -3.663e-01 * t**2
video_b_speed_from_tail_height           (t) = 2.454e+02 + -9.307e+01 * t + 1.141e+01 * t**2
video_b_speed_from_span                  (t) = 1.504e+02 + -5.507e+01 * t + 9.666e+00 * t**2


# plot "video_b_bearings.dat" using 1:5:6:7 title "Bearing data" w yerrorbars, \
    "video_b_bearings.dat" using 1:5 title "Bearings fitted to mid values" lw 2 w line smooth csplines, \
    "video_b_tail_height.dat" using 1:5:6:7 title "Tail height data" w yerrorbars, \
    "video_b_tail_height.dat" using 1:5 title "Tail height fitted to mid values" lw 2 w line smooth csplines, \
    "video_b_span.dat" using 1:5:6:7 title "Span data" w yerrorbars, \
    "video_b_span.dat" using 1:5 title "Span fitted to mid values" lw 2 w line smooth csplines

plot "video_b_bearings.dat" using 1:5:6:7 title "Bearing data" w yerrorbars, \
    "video_b_bearings.dat" using 1:(video_b_speed_from_bearings($1-34.25)) title "Bearings fitted to mid values" lw 2 w line smooth csplines, \
    "video_b_tail_height.dat" using 1:5:6:7 title "Tail height data" w yerrorbars, \
    "video_b_tail_height.dat" using 1:(video_b_speed_from_tail_height($1-34.25)) title "Tail height fitted to mid values" lw 2 w line smooth csplines, \
    "video_b_span.dat" using 1:5:6:7 title "Span data" w yerrorbars, \
    "video_b_span.dat" using 1:(video_b_speed_from_span($1-34.25)) title "Span fitted to mid values" lw 2 w line smooth csplines

# linespoints
#plot "video_b.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "video_b.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "video_b.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
