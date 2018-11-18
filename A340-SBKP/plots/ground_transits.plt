# set logscale x
set colorsequence classic
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
set yrange [1100:-1100] reverse
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

set arrow from 0,0 to 3240,0 nohead lw 20 lc rgb "#C0C0C0" back
set arrow from 73,414 to 3434,-775 lc rgb "#0000FF" lw 0.75 nohead
set label "Tower 1" at 72.8,448.7 right font ",8" rotate by 90
set arrow from 118,413 to 3434,-775 lt -1 lw 0.75 nohead
set label "Tower 2" at 118.5,448.4 right font ",8" rotate by 90
set arrow from 164,413 to 3434,-775 lt -1 lw 0.75 nohead
set label "Tower 3" at 163.9,448.1 right font ",8" rotate by 90
set arrow from 211,412 to 3434,-775 lt -1 lw 0.75 nohead
set label "Tower 4" at 210.6,447.5 right font ",8" rotate by 90
set arrow from 255,412 to 3434,-775 lt -1 lw 0.75 nohead
set label "Tower 5" at 255.4,447.0 right font ",8" rotate by 90
set arrow from 302,411 to 3434,-775 lt -1 lw 0.75 nohead
set label "Tower 6" at 301.5,446.5 right font ",8" rotate by 90
set arrow from 1598,0 to 3434,-775 lt -1 lw 0.75 nohead
set label "Concrete block hut" at 2109.3,-230.6 right font ",8" rotate by 0
set arrow from 951,983 to 3434,-775 lc rgb "#0000FF" lw 0.75 nohead
set label "Control tower base" at 915.9,982.6 right font ",8" rotate by 0
set arrow from 2813,0 to 3434,-775 lt -1 lw 0.75 nohead
set label "Chequer board hut" at 2878.9,-125.4 right font ",8" rotate by 0
set arrow from 2956,0 to 3434,-775 lc rgb "#0000FF" lw 0.75 nohead
set label "Factory interior corner" at 3140.4,-355.7 right font ",8" rotate by 0
set arrow from 2724,382 to 3434,-775 lc rgb "#0000FF" lw 0.75 nohead
set label "Trees right of Fedex" at 2688.6,382.3 right font ",8" rotate by 0
set arrow from 3164,0 to 3434,-775 lt -1 lw 0.75 nohead
set label "Factory extreme left" at 3215.0,-246.2 right font ",8" rotate by 0
set arrow from 3023,813 to 3434,-775 lc rgb "#0000FF" lw 0.75 nohead
set label "Tall radio tower" at 2988.3,812.6 right font ",8" rotate by 0
set arrow from 3239,693 to 3434,-775 lt -1 lw 0.75 nohead
set label "Second control tower" at 3203.8,692.7 right font ",8" rotate by 0
set label "Observer X=3434 ±4m Y=-775 ±6 m" at 2434,-775 right font ",12"
set arrow from 2434,-775 to 3409,-775 lt -1 lw 2 empty

set output "ground_transits.svg"

plot "ground_transits.dat" using 2:3 title "Transit points" ps 1.5, \
    "ground_transits.dat" using 4:5 title "Runway intersection" ps 1.0
reset
