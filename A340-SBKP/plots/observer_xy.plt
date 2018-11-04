# set logscale x
set grid
set xlabel "X (m)"
#set xtics 2100,100,2400
# set xtics 100
set xtics autofreq
set mxtics 2
set xrange [2150:2350]
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

set terminal svg size 600,600

set title "Observers Position [153 observations]"
set label "X=2266 ±13m Y=-763 ±12 m" at 2216,-718 center font ",14"
set arrow from 2226,-726 to 2266,-763 lt -1 lw 2 empty

set output "observer_xy.svg"

plot "observer_xy.dat" using 1:2 title "With -ve error" w points ps 0.5, \
    "observer_xy.dat" using 1:3 title "No error" w points ps 0.5, \
    "observer_xy.dat" using 1:4 title "With +ve error" w points ps 0.5
#plot "observer_xy.dat" using 1:3 title "Mid data" w points lt 6 ps 1
reset
