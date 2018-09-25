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
set yrange [:10]
#set yrange [-600:-900] reverse
#set ytics 100
set ytics autofreq
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

plot "aircraft_yaw.dat" using 1:2:3:4 title "Estimated" w yerrorbars ps 1.25, \
    "aircraft_yaw.dat" using 1:2 title "Fit of best estimate" w linespoints ps 1.25 smooth csplines#bezier
reset
