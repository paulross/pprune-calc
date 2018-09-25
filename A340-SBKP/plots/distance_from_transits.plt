# set logscale x
set grid
# set_title
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance (m)"
# set_yrange
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

set label "Tower 1 t=1.9s ∆d=490" at 1.9,490.4 right font ",6" rotate by 30
set label "Tower 2 t=2.4s ∆d=486" at 2.4,485.9 right font ",6" rotate by 30
set label "Tower 3 t=2.9s ∆d=480" at 2.9,480.5 right font ",6" rotate by 30
set label "Tower 4 t=3.3s ∆d=476" at 3.3,475.9 right font ",6" rotate by 30
set label "Tower 5 t=3.8s ∆d=469" at 3.8,469.5 right font ",6" rotate by 30
set label "Tower 6 t=4.2s ∆d=464" at 4.2,463.7 right font ",6" rotate by 30
set label "Control tower base t=17.2s ∆d=57" at 17.2,57.3 right font ",6" rotate by 30
set label "Chequer board hut t=22.8s ∆d=-74" at 22.8,-73.9 right font ",6" rotate by 30
set label "Factory interior corner t=24.4s ∆d=-157" at 24.4,-156.9 right font ",6" rotate by 30
set label "Trees right of Fedex t=24.4s ∆d=-176" at 24.4,-176.4 right font ",6" rotate by 30
set label "Fedex right t=24.6s ∆d=-135" at 24.6,-134.9 right font ",6" rotate by 30
set label "Fedex left t=24.8s ∆d=-144" at 24.8,-143.9 right font ",6" rotate by 30
set label "Factory extreme left t=26.7s ∆d=-77" at 26.7,-76.9 right font ",6" rotate by 30
set label "Tall radio tower t=27.5s ∆d=-10" at 27.5,-10.3 right font ",6" rotate by 30
set label "Second control tower t=28.6s ∆d=-19" at 28.6,-19.3 right font ",6" rotate by 30

# linespoints
plot "distance_from_transits.dat" using 1:($2-$4) title "From transits" lt 2 lw 1.0 w linespoints, \
    "distance_from_transits.dat" using 1:($3-$4) title "-10 knots" lt 1 lw 1.0 w linespoints, \
    "distance_from_transits.dat" using 1:($5-$4) title "+10 knots" lt 3 lw 1.0 w linespoints
reset
