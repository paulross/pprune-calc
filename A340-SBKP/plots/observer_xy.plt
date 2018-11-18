# set logscale x
set colorsequence classic
set grid
set xlabel "X (m)"
#set xtics 2100,100,2400
# set xtics 100
set xtics autofreq
set mxtics 2
set xrange [3300:3550]
#set format x ""

# set logscale y
set ylabel "Y (m)"
# set yrange [] reverse
set yrange [-650:-850] reverse
# set ytics 100
set ytics autofreq
set mytics 2
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 2
set datafile separator whitespace#"	"
set datafile missing "NaN"

# set key off

set terminal svg size 750,600

set title "Observers Position [153 observations]"
set label "X=3448 ±13m Y=-763 ±12 m" at 3413,-763 right font ",12" textcolor rgb "#007F00"
set arrow from 3414,-763 to 3448,-763 lt -1 lw 2 empty
set arrow from 73,414 to 3670,-856 nohead lw 1.50 lc rgb "#FF00FF"
set label "Tower 1" at 22.8,413.7 right font ",9" rotate by -30
set label "Fence Break 1" at 2206.5,-357.1 right font ",9" rotate by -30
set arrow from 951,983 to 3640,-916 nohead lw 1.50 lc rgb "#FF00FF"
set label "Control tower base" at 900.9,982.6 right font ",9" rotate by -30
set label "Embankment inside corner" at 2626.7,-236.3 right font ",9" rotate by -30
set arrow from 2724,382 to 3563,-989 nohead lw 1.50 lc rgb "#FF00FF"
set label "Trees right of Fedex" at 2673.6,382.3 right font ",9" rotate by -30
set label "Factory interior corner" at 3125.4,-355.7 right font ",9" rotate by -30
set arrow from 2938,389 to 3531,-1005 nohead lw 1.50 lc rgb "#FF00FF"
set label "Factory cream stripe" at 2888.0,389.5 right font ",9" rotate by -30
set label "ALUGAM-SE Left" at 3292.0,-559.9 right font ",9" rotate by -30
set arrow from 3023,813 to 3498,-1016 nohead lw 1.50 lc rgb "#FF00FF"
set label "Tall radio tower" at 2973.3,812.6 right font ",9" rotate by -30
set label "Building corner" at 3220.4,-140.3 right font ",9" rotate by -30
set arrow from 64,390 to 3688,-802 nohead lw 1.50 lc rgb "#00D0D0" dt 4
set arrow from 937,962 to 3669,-873 nohead lw 1.50 lc rgb "#00D0D0" dt 4
set arrow from 2702,369 to 3620,-951 nohead lw 1.50 lc rgb "#00D0D0" dt 4
set arrow from 2915,380 to 3575,-984 nohead lw 1.50 lc rgb "#00D0D0" dt 4
set arrow from 2999,806 to 3566,-996 nohead lw 1.50 lc rgb "#00D0D0" dt 4
set arrow from 81,437 to 3650,-910 nohead lw 1.50 lc rgb "#D0D000" dt 4
set arrow from 965,1003 to 3609,-959 nohead lw 1.50 lc rgb "#D0D000" dt 4
set arrow from 2745,395 to 3504,-1022 nohead lw 1.50 lc rgb "#D0D000" dt 4
set arrow from 2961,399 to 3486,-1022 nohead lw 1.50 lc rgb "#D0D000" dt 4
set arrow from 3047,819 to 3428,-1032 nohead lw 1.50 lc rgb "#D0D000" dt 4
set label "X=3434 ±6m Y=-775 ±9 m" at 3399,-775 right font ",12" textcolor rgb "#FF00FF"
set arrow from 3400,-775 to 3434,-775 lt -1 lw 2 empty

set output "observer_xy.svg"

plot "observer_xy.dat" using 1:2 title "With -ve error" w points ps 0.5, \
    "observer_xy.dat" using 1:3 title "No error" w points ps 1.0, \
    "observer_xy.dat" using 1:4 title "With +ve error" w points ps 0.5
#plot "observer_xy.dat" using 1:3 title "Mid data" w points lt 6 ps 1
reset
