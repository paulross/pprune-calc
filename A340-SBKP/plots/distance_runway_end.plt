# set logscale x
set grid
set title "Distance from runway start."
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance (m)"
set yrange [*:*]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "distance_runway_end.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# Start distance arrows and labels
set arrow from -30.057,1000 to -30.057,537.333 lt 1
set arrow from -32.829,1200 to -32.829,232.350 lt 2
set arrow from -35.571,1400 to -35.571,-86.825 lt 3
set label "Calculated start at -30.1s, 537m" at -30.1,1100 left font ",9"
set label "Calculated start at -32.8s, 232m" at -32.8,1300 left font ",9"
set label "Calculated start at -35.6s, -87m" at -35.6,1500 left font ",9"
# End labels at start of take off
# Labels at t=0
set arrow from 6.000,1324.7 to 0.0,1324.700 lt 1
set label "t=0.0s, d=1325m" at 6.0,1324.7 left font ",9"
set arrow from 6.000,1181.6 to 0.0,1181.593 lt 2
set label "t=0.0s, d=1182m" at 6.0,1181.6 left font ",9"
set arrow from 6.000,1038.5 to 0.0,1038.486 lt 3
set label "t=0.0s, d=1038m" at 6.0,1038.5 left font ",9"
# End labels at t=0
set arrow from 27.800,2290 to 27.800,3140 lt -1
set label "End asphalt 27.8s" at 27.8,2190 center font ",10"
set arrow from 17.800,3240.000 to 27.800,3240.000 lt 2
set label "3240m" at 16.8,3240.0 right font ",10"
# End video
set arrow from 35.667,2850 to 35.667,3700 lt -1
set label "End video 35.7s" at 35.7,2750 center font ",10"

# linespoints
plot "distance_runway_end.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "distance_runway_end.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "distance_runway_end.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
