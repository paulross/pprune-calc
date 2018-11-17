# set logscale x
set grid
set title "Distances down runway comparing estimates with transits."
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance Compared to Mid Estimate (m)"
# set yrange [-250:250]
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
#  lw 2 pointsize 2

set label "Tower 1 t=2.2s ∆d=-72" at 2.2,-72.4 right font ",6" rotate by 40
set label "Tower 2 t=2.7s ∆d=-71" at 2.7,-71.2 right font ",6" rotate by 40
set label "Tower 3 t=3.1s ∆d=-70" at 3.1,-70.3 right font ",6" rotate by 40
set label "Tower 4 t=3.6s ∆d=-69" at 3.6,-68.5 right font ",6" rotate by 40
set label "Tower 5 t=4.0s ∆d=-69" at 4.0,-69.0 right font ",6" rotate by 40
set label "Tower 6 t=4.5s ∆d=-68" at 4.5,-68.0 right font ",6" rotate by 40
set label "Tower 7 t=6.6s ∆d=85" at 6.6,85.3 right font ",6" rotate by 40
set label "Concrete block hut t=7.3s ∆d=-75" at 7.3,-75.5 right font ",6" rotate by 40
set label "Tower 8 t=8.0s ∆d=18" at 8.0,18.4 right font ",6" rotate by 40
set label "Tower 9 t=8.7s ∆d=-1" at 8.7,-1.2 right font ",6" rotate by 40
set label "Tower 10 t=9.3s ∆d=-20" at 9.3,-20.2 right font ",6" rotate by 40
set label "Tower 11 t=10.0s ∆d=-43" at 10.0,-42.5 right font ",6" rotate by 40
set label "Tower 12 t=10.6s ∆d=-63" at 10.6,-63.1 right font ",6" rotate by 40
set label "Tower 13 t=11.3s ∆d=16" at 11.3,16.4 right font ",6" rotate by 40
set label "Tower 14 t=11.8s ∆d=-3" at 11.8,-3.1 right font ",6" rotate by 40
set label "Tower 15 t=12.2s ∆d=-10" at 12.2,-9.7 right font ",6" rotate by 40
set label "Tower 16 t=12.8s ∆d=-37" at 12.8,-37.2 right font ",6" rotate by 40
set label "Tower 17 t=13.4s ∆d=-62" at 13.4,-62.4 right font ",6" rotate by 40
set label "Tower 18 t=15.3s ∆d=-185" at 15.3,-185.0 right font ",6" rotate by 40
set label "Tower 19 t=16.2s ∆d=-236" at 16.2,-235.7 right font ",6" rotate by 40
set label "Control tower base t=17.4s ∆d=-38" at 17.4,-37.9 right font ",6" rotate by 40
set label "Chequer board hut t=23.0s ∆d=-44" at 23.0,-44.2 right font ",6" rotate by 40
set label "Factory interior corner t=24.6s ∆d=-54" at 24.6,-53.8 right font ",6" rotate by 40
set label "Trees right of Fedex t=24.6s ∆d=-25" at 24.6,-25.4 right font ",6" rotate by 40
set label "Fedex right t=24.8s ∆d=-27" at 24.8,-26.7 right font ",6" rotate by 40
set label "Fedex left t=25.1s ∆d=-38" at 25.1,-37.8 right font ",6" rotate by 40
set label "Factory extreme left t=26.9s ∆d=-41" at 26.9,-41.1 right font ",6" rotate by 40
set label "Tall radio tower t=27.8s ∆d=-26" at 27.8,-25.9 right font ",6" rotate by 40
set label "Second control tower t=28.8s ∆d=-26" at 28.8,-26.5 right font ",6" rotate by 40

# linespoints
plot "distance_from_transits.dat" using 1:($3-$4) title "Mid estimate -10 knots" lt 1 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($4-$4) title "Mid estimate" lt 2 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($5-$4) title "Mid estimate +10 knots" lt 3 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($2-$4) title "From transits" lt 2 lw 1.5 ps 1.25 w points
reset
