# set logscale x
set grid
set title "Acceleration."
set xlabel "Video Time (seconds)"
set xtics
#set format x ""

# set logscale y
set ylabel "Acceleration (knots/s)"
# set yrange [:110]
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
#fit cost(x) "acceleration.dat" using 1:2 via a,b

set terminal svg size 700,500           # choose the file format

set output "acceleration.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# linespoints
plot "acceleration.dat" using 1:2 title "Acceleration from best fit of ground speed" lt 2 lw 2 w lines
#    "acceleration.dat" using 1:3 title "Acceleration (Min)" lw 2 w lines, \
#    "acceleration.dat" using 1:4 title "Acceleration (Max)" lw 2 w lines
reset
