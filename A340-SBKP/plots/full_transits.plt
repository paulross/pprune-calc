# set logscale x
set colorsequence classic
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
# set yrange [-1400:1100] reverse
set yrange [1100:-1400]
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

set terminal svg size 1200,600

set arrow from 0,0 to 3240,0 nohead lw 20 lc rgb "#C0C0C0" back
set label "t=2.4s x=1243m" at 1223,-20 right font ",9" textcolor rgb "#007F00" rotate by -30 front
set label "t=17.7s x=2339m" at 2319,-20 right font ",9" textcolor rgb "#007F00" rotate by -30 front
set label "t=24.9s x=2958m" at 2938,-20 right font ",9" textcolor rgb "#007F00" rotate by -30 front
set label "t=26.6s x=3104m" at 3084,-20 right font ",9" textcolor rgb "#007F00" rotate by -30 front
set label "t=28.0s x=3233m" at 3213,-20 right font ",9" textcolor rgb "#007F00" rotate by -30 front
set arrow from 73,414 to 3670,-856 nohead lw 0.75 lc rgb "#0000FF"
set label "Tower 1" at 22.8,413.7 right font ",9" rotate by -30
set label "Fence Break 1" at 2206.5,-357.1 right font ",9" rotate by -30
set arrow from 951,983 to 3640,-916 nohead lw 0.75 lc rgb "#0000FF"
set label "Control tower base" at 900.9,982.6 right font ",9" rotate by -30
set label "Embankment inside corner" at 2626.7,-236.3 right font ",9" rotate by -30
set arrow from 2724,382 to 3563,-989 nohead lw 0.75 lc rgb "#0000FF"
set label "Trees right of Fedex" at 2673.6,382.3 right font ",9" rotate by -30
set label "Factory interior corner" at 3125.4,-355.7 right font ",9" rotate by -30
set arrow from 2938,389 to 3531,-1005 nohead lw 0.75 lc rgb "#0000FF"
set label "Factory cream stripe" at 2888.0,389.5 right font ",9" rotate by -30
set label "ALUGAM-SE Left" at 3292.0,-559.9 right font ",9" rotate by -30
set arrow from 3023,813 to 3498,-1016 nohead lw 0.75 lc rgb "#0000FF"
set label "Tall radio tower" at 2973.3,812.6 right font ",9" rotate by -30
set label "Building corner" at 3220.4,-140.3 right font ",9" rotate by -30
set label "X=3434 ±6m Y=-775 ±9 m" at 2924,-885 right font ",12"
set arrow from 2934,-875 to 3434,-775 lt -1 lw 2 empty

set output "full_transits.svg"

plot "full_transits.dat" using 2:3 title "Transit points" ps 1.5, \
    "full_transits.dat" using 4:5 title "Runway intersection" ps 1.0
reset
