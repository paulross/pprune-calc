# set logscale x
set grid
set title "Full Transits to Observer"
set xlabel "Distance from start of runway (m)"
#set xtics 2100,100,2400
set xtics 500
#set xtics autofreq
set xrange [0:3700]
# set xrange [2250:3700]
#set format x ""

# set logscale y
set ylabel "Distance from runway centerline (+ve right, -ve left)"
set yrange [-1400:1100] reverse
# set yrange [400:-800] reverse
#set yrange [:10]
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
set arrow from 121,706 to 3649,-927 nohead lw 0.75 lc rgb "#0000FF"
set label "Tower 8" at 71.2,705.9 right font ",8" rotate by 0
set label "Concrete block hut" at 2094.3,-230.6 right font ",8" rotate by 0
set arrow from 2720,427 to 3548,-995 nohead lw 0.75 lc rgb "#0000FF"
set label "Trees right of Fedex" at 2669.6,427.4 right font ",8" rotate by 0
set label "Concrete block hut" at 3125.4,-355.7 right font ",8" rotate by 0
set arrow from 3023,813 to 3496,-1009 nohead lw 0.75 lc rgb "#0000FF"
set label "Tall radio tower" at 2973.3,812.6 right font ",8" rotate by 0
set label "Building corner" at 3220.4,-140.3 right font ",8" rotate by 0

set output "full_transits.svg"

plot "full_transits.dat" using 2:3 title "Transit points" ps 1.5, \
    "full_transits.dat" using 4:5 title "Runway intersection" ps 1.0
reset
