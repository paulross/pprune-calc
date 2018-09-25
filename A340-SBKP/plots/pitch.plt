# set logscale x
set grid
set title "Pitch Angle."
set xlabel "Time (s)"
#set xrange [0:3000]
#set xtics
#set format x ""

# set logscale y
set ylabel "Pitch (degrees)"
#set yrange [100:-1000]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

# Curve fit
#cost(x) = a + (b / (x/1024))
#fit cost(x) "pitch.dat" using 1:2 via a,b

set terminal svg size 700,500           # choose the file format

set key off

set output "pitch.svg"   # choose the output device

set arrow from 18,-1.5 to 23,5.7 lw 3.5 lc rgb "blue"
set label 1 "1.4 °/s" at 21.5,2.5 font ",14"

set arrow from 29,6.7 to 31,9.5 lw 3.5 lc rgb "blue"
set label 2 "1.4 °/s" at 30.5,7.5 font ",14"

# Nose wheel off at around 00:17:27 i.e. 17.9s
set arrow from 17.9,6 to 17.9,0 lw 2 lc rgb "black"
set label 3 "Nose wheel off" at 17.9,6.5 font ",12" center

# Main gear off at around 00:25:19 i.e. 25.63
set arrow from 25.6,10.5 to 25.6,8 lw 2 lc rgb "black"
set label 4 "Main wheels off" at 25.6,11 font ",12" center

# plot "pitch.dat" using 1:4 title "Bearing" lw 2 w linespoints
plot "pitch.dat" using 1:2:3:4:5:6 title "Raw data" w xyerrorbars lw 1.5#, \
    "pitch.dat" using 1:2 with lines smooth bezier

reset
