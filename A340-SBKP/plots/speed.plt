# set logscale x
set grid
set title "Speed."
set xlabel "Time (seconds)"
set xtics
#set format x ""

# set logscale y
set ylabel "Speed (m/s)."
# set yrange [8:35]
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
#fit cost(x) "{file_name}.dat" using 1:2 via a,b

set terminal svg size 750,550           # choose the file format

set output "speed.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

plot "speed.dat" using 1:2:3:4:5:6 w xyerrorbars # ( x, y, xlow, xhigh, ylow, yhigh )
reset
