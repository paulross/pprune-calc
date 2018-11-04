# set logscale x
set grid
set title "Distances down runway comparing estimates with transits."
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance Compared to Mid Estimate (m)"
set yrange [-250:250]
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

set label "Tower 1 t=2.2s ∆d=-50" at 2.2,-50.2 right font ",6" rotate by 40
set label "Tower 2 t=2.7s ∆d=-49" at 2.7,-49.3 right font ",6" rotate by 40
set label "Tower 3 t=3.1s ∆d=-49" at 3.1,-48.7 right font ",6" rotate by 40
set label "Tower 4 t=3.6s ∆d=-47" at 3.6,-47.1 right font ",6" rotate by 40
set label "Tower 5 t=4.0s ∆d=-48" at 4.0,-47.9 right font ",6" rotate by 40
set label "Tower 6 t=4.5s ∆d=-47" at 4.5,-47.1 right font ",6" rotate by 40
set label "Control tower base t=17.4s ∆d=-19" at 17.4,-18.7 right font ",6" rotate by 40
set label "Chequer board hut t=23.0s ∆d=-43" at 23.0,-43.4 right font ",6" rotate by 40
set label "Factory interior corner t=24.6s ∆d=-61" at 24.6,-60.9 right font ",6" rotate by 40
set label "Trees right of Fedex t=24.6s ∆d=-199" at 24.6,-199.2 right font ",6" rotate by 40
set label "Fedex right t=24.8s ∆d=-156" at 24.8,-155.6 right font ",6" rotate by 40
set label "Fedex left t=25.1s ∆d=-164" at 25.1,-163.9 right font ",6" rotate by 40
set label "Factory extreme left t=26.9s ∆d=-40" at 26.9,-39.8 right font ",6" rotate by 40
set label "Tall radio tower t=27.8s ∆d=-19" at 27.8,-19.0 right font ",6" rotate by 40
set label "Second control tower t=28.8s ∆d=-21" at 28.8,-20.9 right font ",6" rotate by 40

# linespoints
plot "distance_from_transits.dat" using 1:($3-$4) title "Speed error: -10 knots" lt 1 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($4-$4) title "Speed error: 0 knots" lt 2 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($5-$4) title "Speed error: +10 knots" lt 3 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($2-$4) title "From transits" lt 2 lw 1.5 ps 1.25 w points
reset
