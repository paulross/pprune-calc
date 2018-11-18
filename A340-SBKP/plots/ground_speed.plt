# set logscale x
set colorsequence classic
set grid
set title "Ground Speed."
set xlabel "Video Time (seconds)"
set xtics
#set format x ""

# set logscale y
set ylabel "Ground Speed (knots)"
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
#fit cost(x) "ground_speed.dat" using 1:2 via a,b

set terminal svg size 700,500           # choose the file format

set output "ground_speed.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# linespoints
plot "ground_speed.dat" using 1:2:3:4:5:6 title "Raw data" w xyerrorbars, \
    "ground_speed.dat" using 1:7 title "Fitted to mid values" lw 2 w line

#    "ground_speed.dat" using 1:8 title "Fitted to extreme minimum values" lw 1 w line, \
#    "ground_speed.dat" using 1:9 title "Fitted to extreme maximum values" lw 1 w line
reset
