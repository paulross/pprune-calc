# set logscale x
set grid
set title "Transits to Observer"
set xlabel "Distance from start of runway (m)"
#set xtics 2100,100,2400
set xtics 500
#set xtics autofreq
set xrange [0:3700]
#set format x ""

# set logscale y
set ylabel "Distance from runway centerline (+ve right, -ve left)"
set yrange [-1100:1100] reverse
#set yrange [:10]
#set yrange [-600:-900] reverse
set ytics 200
#set ytics autofreq
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

set arrow from 0,0 to 3240,0 nohead lw 20 lc rgb "#C0C0C0"
set arrow from 80,707 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 125,708 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 171,708 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 216,710 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 262,710 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 308,710 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 960,988 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 2789,0 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 2844,0 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 2453,385 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 2536,397 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 2560,395 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 3130,0 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 3032,815 to 3458,-656 lt -1 lw 0.75 nohead
set arrow from 3247,695 to 3458,-656 lt -1 lw 0.75 nohead

set output "ground_transits.svg"

plot "ground_transits.dat" using 2:3 title "Transit points" ps 1.5, \
    "ground_transits.dat" using 4:5 title "Runway intersection" ps 1.0
reset
