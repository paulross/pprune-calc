# set logscale x
set grid
set title "Aircraft Deviation from Runway Heading"
set xlabel "Video Time (s)"
#set xtics 2100,100,2400
set xtics autofreq
#set xrange [2000:2500]
#set format x ""

# set logscale y
set ylabel "Deviation (degrees, +ve right, -ve left)"
set yrange [:8]
#set yrange [-600:-900] reverse
set ytics 1
# set mytics 0.5
# set ytics autofreq
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 2
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set key off

set terminal svg size 800,600

set output "aircraft_yaw.svg"


# Nose wheel off at around 00:17:27 i.e. 17.9s
set arrow from 17.9,-4.5 to 17.9,0.0 lw 2 lc rgb "black"
set label 3 "Nose wheel off" at 17.9,-5 font ",12" center

# Main gear off at around 00:25:19 i.e. 25.63
set arrow from 25.6,-4.5 to 25.6,0.5 lw 2 lc rgb "black"
set label 4 "Main wheels off" at 25.6,-5 font ",12" center

# linespoints  ps 1.25
plot "aircraft_yaw.dat" using 1:2:3:4 title "Estimated" w yerrorbars ps 1.25, \
    "aircraft_yaw.dat" using 1:2 title "Fit of estimate" w lines lw 2 smooth bezier# csplines#bezier
reset
