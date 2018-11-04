# set logscale x
set grid
set title "Transits to Observer"
set xlabel "Distance from start of runway (m)"
#set xtics 2100,100,2400
set xtics 500
#set xtics autofreq
set xrange [0:3700]
# set xrange [2250:3700]
#set format x ""

# set logscale y
set ylabel "Distance from runway centerline (+ve right, -ve left)"
set yrange [-1100:1100] reverse
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
set arrow from 75,415 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 1" at 50.2,439.9 right font ",8" rotate by 60
set arrow from 121,415 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 2" at 95.9,439.5 right font ",8" rotate by 60
set arrow from 166,414 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 3" at 141.4,439.3 right font ",8" rotate by 60
set arrow from 213,414 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 4" at 188.2,438.7 right font ",8" rotate by 60
set arrow from 258,413 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 5" at 233.0,438.2 right font ",8" rotate by 60
set arrow from 304,413 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 6" at 279.2,437.6 right font ",8" rotate by 60
set arrow from 80,707 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 7" at 54.6,731.7 right font ",8" rotate by 60
set arrow from 125,708 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 8" at 100.3,732.9 right font ",8" rotate by 60
set arrow from 171,708 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 9" at 146.3,733.4 right font ",8" rotate by 60
set arrow from 216,710 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 10" at 191.2,734.5 right font ",8" rotate by 60
set arrow from 262,710 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 11" at 236.9,734.8 right font ",8" rotate by 60
set arrow from 308,710 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 12" at 282.6,735.1 right font ",8" rotate by 60
set arrow from 97,942 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 13" at 72.3,967.1 right font ",8" rotate by 60
set arrow from 143,942 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 14" at 117.8,966.8 right font ",8" rotate by 60
set arrow from 188,942 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 15" at 163.1,966.5 right font ",8" rotate by 60
set arrow from 233,942 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 16" at 207.9,966.6 right font ",8" rotate by 60
set arrow from 279,941 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 17" at 253.7,966.5 right font ",8" rotate by 60
set arrow from 324,941 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 18" at 298.8,965.9 right font ",8" rotate by 60
set arrow from 368,941 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 19" at 342.9,966.5 right font ",8" rotate by 60
set arrow from 958,985 to 3448,-763 lt -1 lw 0.75 nohead
set label "Control tower base" at 932.7,1010.4 right font ",8" rotate by 60
set arrow from 2813,0 to 3448,-763 lt -1 lw 0.75 nohead
set label "Chequer board hut" at 2787.6,25.0 right font ",8" rotate by 60
set arrow from 2941,0 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Factory interior corner" at 2915.7,25.0 right font ",8" rotate by 60
set arrow from 2453,385 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Trees right of Fedex" at 2428.0,409.5 right font ",8" rotate by 60
set arrow from 2536,397 to 3448,-763 lt -1 lw 0.75 nohead
set label "Fedex right" at 2510.5,421.9 right font ",8" rotate by 60
set arrow from 2560,395 to 3448,-763 lt -1 lw 0.75 nohead
set label "Fedex left" at 2535.0,420.1 right font ",8" rotate by 60
set arrow from 3160,0 to 3448,-763 lt -1 lw 0.75 nohead
set label "Factory extreme left" at 3135.0,25.0 right font ",8" rotate by 60
set arrow from 3032,815 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tall radio tower" at 3007.1,840.0 right font ",8" rotate by 60
set arrow from 3247,695 to 3448,-763 lt -1 lw 0.75 nohead
set label "Second control tower" at 3222.3,719.7 right font ",8" rotate by 60
set label "Observer X=2266 ±13m Y=-763 ±12 m" at 2448,-763 right font ",12"
set arrow from 2448,-763 to 3423,-763 lt -1 lw 2 empty

set output "ground_transits.svg"

plot "ground_transits.dat" using 2:3 title "Transit points" ps 1.5, \
    "ground_transits.dat" using 4:5 title "Runway intersection" ps 1.0
reset
