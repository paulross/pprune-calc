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
set arrow from 73,414 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Tower 1" at 47.8,438.7 right font ",8" rotate by 60
set arrow from 118,413 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 2" at 93.5,438.4 right font ",8" rotate by 60
set arrow from 164,413 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 3" at 138.9,438.1 right font ",8" rotate by 60
set arrow from 211,412 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 4" at 185.6,437.5 right font ",8" rotate by 60
set arrow from 255,412 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 5" at 230.4,437.0 right font ",8" rotate by 60
set arrow from 302,411 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 6" at 276.5,436.5 right font ",8" rotate by 60
set arrow from 76,705 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 7" at 50.6,729.7 right font ",8" rotate by 60
set arrow from 1579,0 to 3448,-763 lt -1 lw 0.75 nohead
set label "Concrete block hut" at 1554.4,25.0 right font ",8" rotate by 60
set arrow from 121,706 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 8" at 96.2,730.9 right font ",8" rotate by 60
set arrow from 167,706 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 9" at 142.1,731.4 right font ",8" rotate by 60
set arrow from 212,708 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 10" at 187.0,732.5 right font ",8" rotate by 60
set arrow from 258,708 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 11" at 232.6,732.8 right font ",8" rotate by 60
set arrow from 303,708 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 12" at 278.3,733.1 right font ",8" rotate by 60
set arrow from 92,939 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 13" at 66.9,964.4 right font ",8" rotate by 60
set arrow from 137,939 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 14" at 112.4,964.1 right font ",8" rotate by 60
set arrow from 183,939 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 15" at 157.6,963.8 right font ",8" rotate by 60
set arrow from 227,939 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 16" at 202.4,963.9 right font ",8" rotate by 60
set arrow from 273,939 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 17" at 248.1,963.8 right font ",8" rotate by 60
set arrow from 318,938 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 18" at 293.2,963.3 right font ",8" rotate by 60
set arrow from 362,939 to 3448,-763 lt -1 lw 0.75 nohead
set label "Tower 19" at 337.2,963.8 right font ",8" rotate by 60
set arrow from 951,983 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Control tower base" at 925.9,1007.6 right font ",8" rotate by 60
set arrow from 2809,0 to 3448,-763 lt -1 lw 0.75 nohead
set label "Chequer board hut" at 2783.8,25.0 right font ",8" rotate by 60
set arrow from 2937,0 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Factory interior corner" at 2912.1,25.0 right font ",8" rotate by 60
set arrow from 2724,382 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Trees right of Fedex" at 2698.6,407.3 right font ",8" rotate by 60
set arrow from 2746,385 to 3448,-763 lt -1 lw 0.75 nohead
set label "Fedex right" at 2721.2,409.8 right font ",8" rotate by 60
set arrow from 2765,384 to 3448,-763 lt -1 lw 0.75 nohead
set label "Fedex left" at 2739.9,409.4 right font ",8" rotate by 60
set arrow from 3156,0 to 3448,-763 lt -1 lw 0.75 nohead
set label "Factory extreme left" at 3130.5,25.0 right font ",8" rotate by 60
set arrow from 3023,813 to 3448,-763 lc rgb "#0000FF" lw 0.75 nohead
set label "Tall radio tower" at 2998.3,837.6 right font ",8" rotate by 60
set arrow from 3239,693 to 3448,-763 lt -1 lw 0.75 nohead
set label "Second control tower" at 3213.8,717.7 right font ",8" rotate by 60
set label "Observer X=2266 ±13m Y=-763 ±12 m" at 2448,-763 right font ",12"
set arrow from 2448,-763 to 3423,-763 lt -1 lw 2 empty

set output "ground_transits.svg"

plot "ground_transits.dat" using 2:3 title "Transit points" ps 1.5, \
    "ground_transits.dat" using 4:5 title "Runway intersection" ps 1.0
reset
