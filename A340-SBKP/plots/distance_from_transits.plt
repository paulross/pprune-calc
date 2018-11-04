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

set label "Tower 1 t=2.2s ∆d=-69" at 2.2,-68.8 right font ",6" rotate by 40
set label "Tower 2 t=2.7s ∆d=-68" at 2.7,-67.6 right font ",6" rotate by 40
set label "Tower 3 t=3.1s ∆d=-67" at 3.1,-66.7 right font ",6" rotate by 40
set label "Tower 4 t=3.6s ∆d=-65" at 3.6,-64.9 right font ",6" rotate by 40
set label "Tower 5 t=4.0s ∆d=-65" at 4.0,-65.4 right font ",6" rotate by 40
set label "Tower 6 t=4.5s ∆d=-64" at 4.5,-64.4 right font ",6" rotate by 40
set label "Tower 7 t=6.6s ∆d=90" at 6.6,89.6 right font ",6" rotate by 40
set label "Tower 8 t=8.0s ∆d=23" at 8.0,22.7 right font ",6" rotate by 40
set label "Tower 9 t=8.7s ∆d=3" at 8.7,3.1 right font ",6" rotate by 40
set label "Tower 10 t=9.3s ∆d=-16" at 9.3,-15.9 right font ",6" rotate by 40
set label "Tower 11 t=10.0s ∆d=-38" at 10.0,-38.2 right font ",6" rotate by 40
set label "Tower 12 t=10.6s ∆d=-59" at 10.6,-58.8 right font ",6" rotate by 40
set label "Tower 13 t=11.3s ∆d=21" at 11.3,20.9 right font ",6" rotate by 40
set label "Tower 14 t=11.8s ∆d=1" at 11.8,1.4 right font ",6" rotate by 40
set label "Tower 15 t=12.2s ∆d=-5" at 12.2,-5.2 right font ",6" rotate by 40
set label "Tower 16 t=12.8s ∆d=-33" at 12.8,-32.7 right font ",6" rotate by 40
set label "Tower 17 t=13.4s ∆d=-58" at 13.4,-57.9 right font ",6" rotate by 40
set label "Tower 18 t=15.3s ∆d=-181" at 15.3,-180.5 right font ",6" rotate by 40
set label "Tower 19 t=16.2s ∆d=-231" at 16.2,-231.2 right font ",6" rotate by 40
set label "Control tower base t=17.4s ∆d=-33" at 17.4,-33.4 right font ",6" rotate by 40
set label "Chequer board hut t=23.0s ∆d=-40" at 23.0,-40.3 right font ",6" rotate by 40
set label "Factory interior corner t=24.6s ∆d=-50" at 24.6,-49.8 right font ",6" rotate by 40
set label "Trees right of Fedex t=24.6s ∆d=-205" at 24.6,-204.6 right font ",6" rotate by 40
set label "Fedex right t=24.8s ∆d=-161" at 24.8,-160.6 right font ",6" rotate by 40
set label "Fedex left t=25.1s ∆d=-169" at 25.1,-168.7 right font ",6" rotate by 40
set label "Factory extreme left t=26.9s ∆d=-36" at 26.9,-36.4 right font ",6" rotate by 40
set label "Tall radio tower t=27.8s ∆d=-22" at 27.8,-21.5 right font ",6" rotate by 40
set label "Second control tower t=28.8s ∆d=-22" at 28.8,-22.1 right font ",6" rotate by 40

# linespoints
plot "distance_from_transits.dat" using 1:($3-$4) title "Mid estimate -10 knots" lt 1 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($4-$4) title "Mid estimate" lt 2 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($5-$4) title "Mid estimate +10 knots" lt 3 lw 1.5 w lines, \
    "distance_from_transits.dat" using 1:($2-$4) title "From transits" lt 2 lw 1.5 ps 1.25 w points
reset
