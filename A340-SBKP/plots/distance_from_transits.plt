# set logscale x
set colorsequence classic
set grid
set title "Distances down runway comparing estimates with transits."
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance Compared to Mid Estimate (m)"
set yrange [-150:100]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "distance_from_transits.svg"   # choose the output device
#set key title "Window Length"
set key box
#  lw 2 pointsize 2

set label "Tower 1 t=1.9s ∆d=-76" at 1.9,-75.6 right font ",6" rotate by -35
set label "Tower 2 t=2.4s ∆d=-74" at 2.4,-74.3 right font ",6" rotate by -35
set label "Tower 3 t=2.9s ∆d=-73" at 2.9,-73.3 right font ",6" rotate by -35
set label "Tower 4 t=3.3s ∆d=-71" at 3.3,-71.3 right font ",6" rotate by -35
set label "Tower 5 t=3.8s ∆d=-72" at 3.8,-71.6 right font ",6" rotate by -35
set label "Tower 6 t=4.2s ∆d=-70" at 4.2,-70.5 right font ",6" rotate by -35
set label "Concrete block hut t=7.1s ∆d=-44" at 7.1,-43.8 right font ",6" rotate by -35
set label "Control tower base t=17.2s ∆d=-42" at 17.2,-41.9 right font ",6" rotate by -35
set label "Chequer board hut t=22.8s ∆d=-26" at 22.8,-26.1 right font ",6" rotate by -35
set label "Factory interior corner t=24.4s ∆d=-21" at 24.4,-21.4 right font ",6" rotate by -35
set label "Trees right of Fedex t=24.4s ∆d=-19" at 24.4,-19.2 right font ",6" rotate by -35
set label "Factory extreme left t=26.7s ∆d=-19" at 26.7,-18.9 right font ",6" rotate by -35
set label "Tall radio tower t=27.5s ∆d=-22" at 27.5,-21.5 right font ",6" rotate by -35
set label "Second control tower t=28.6s ∆d=-21" at 28.6,-20.7 right font ",6" rotate by -35

# linespoints
#plot "distance_from_transits.dat" using 1:($3-$4) title "Mid estimate -10 knots" lt 1 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($4-$4) title "Mid estimate" lt 2 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($5-$4) title "Mid estimate +10 knots" lt 3 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($2-$4) title "From transits" lt 2 lw 1.5 ps 1.25 w points
plot "distance_from_transits.dat" using 1:($4-$4) title "Mid estimate" lt 2 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($2-$4) title "From transits" lt 3 lw 1.5 ps 1.25 w points, \
    "distance_from_transits.dat" using 1:(0.5*($5-$4)) title "Mid estimate +5 knots" lt 3 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:(0.5*($5-$4)+25) title "Mid estimate +5 knots +25m" lt 1 lw 1.0 w lines, \
    "distance_from_transits.dat" using 1:(0.5*($5-$4)-25) title "Mid estimate +5 knots -25m" lt 1 lw 1.0 w lines
reset
