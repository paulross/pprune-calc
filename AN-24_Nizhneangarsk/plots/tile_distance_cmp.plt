# set logscale x
set colorsequence classic
set grid
set title "Comparison of Distance From Runway Threshold by Two Methods."
set xlabel "Video Time (s)"
set xtics
set xrange [27:31.5]
#set format x ""

# set logscale y
set ylabel "Distance (m)"
set yrange [-50:400]
# set ytics 8,35,3
# set logscale y2
set y2label "Difference (m)"
set y2range [-6:3]
set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "tile_distance_cmp.svg"   # choose the output device
#set key title "Window Length"
set key left top
#  lw 2 pointsize 2

# Start distance arrows and labels
#set arrow from -30.059,0 to -30.059,-787.468 lt 1
#set label "Calculated start at -30.1s, -787m" at -30.1,100 left font ",9"

# d coefficients: -2.481e+03, 8.276e+01, 5.914e-01, -1.173e-02
tile_distance(t) = -2.481e+03 + 8.276e+01 * t + 5.914e-01 * t**2 + -1.173e-02 * t**3
# Integral of v coefficients: 2.843e+02, -1.645e+01, 4.789e-01, -4.952e-03
# With offset of 4217.960402389347
slab_distance(t) = -4218.0 + t * (2.843e+02 + t * (-1.645e+01 / 2.0 + t * (4.789e-01 / 3.0 + t * -4.952e-03 / 4.0)))


plot "tile_distance_data.dat" using 2:3:4:5 title "Aerial data" w yerrorbars, \
    "tile_distance_data.dat" using 2:(tile_distance($2)) title "Fitted to mid values" lw 2 w line, \
    "slab_speed_data.dat" using 2:6:7:8 title "Slab data" w yerrorbars, \
    "slab_speed_data.dat" using 2:(slab_distance($2)) title "Fitted to mid values" lw 2 w line, \
    "slab_speed_data.dat" using 2:(slab_distance($2) - tile_distance($2)) title "Difference (right)" axes x1y2 lw 2 dt 4 w line

# linespoints
#plot "tile_distance_data.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "tile_distance_data.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "tile_distance_data.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
