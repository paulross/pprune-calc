# set logscale x
set grid
set title "Ground Speed."
set xlabel "Video Time (seconds)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Ground Speed (knots)"
# set yrange [-25:125]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "ground_speed_extrapolated.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

set arrow from -30.057,50 to -30.057,0.000 lt 1
set label "t=-30.1s" at -32.1,54 left font ",12"
set arrow from -32.829,75 to -32.829,0.000 lt 2
set label "t=-32.8s" at -34.8,79 left font ",12"
set arrow from -35.570,100 to -35.570,0.000 lt 3
set label "t=-35.6s" at -37.6,104 left font ",12"

# linespoints
plot "ground_speed_extrapolated.dat" using 1:2:3:4:5:6 title "Raw data" w xyerrorbars, \
    "ground_speed_extrapolated.dat" using 1:7 title "Fitted to mid values" lt 2 lw 2 w lines, \
    "ground_speed_extrapolated.dat" using 1:8 title "-10 knots" lt 1 lw 0.5 w lines, \
    "ground_speed_extrapolated.dat" using 1:9 title "+10 knots" lt 3 lw 0.5 w lines
reset
