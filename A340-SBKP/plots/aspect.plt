# set logscale x
set colorsequence classic
set grid
set title "Bearings to Observer."
set xlabel "Time (s)"
set mxtics 5
#set xrange [0:3000]
#set xtics
#set format x ""

# set logscale y
set ylabel "Bearing (degrees)"
#set yrange [100:-1000]
set ytics 20
set mytics 2
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
#fit cost(x) "aspect.dat" using 1:2 via a,b

set terminal svg size 1000,500           # choose the file format

# set key off

set output "aspect.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# fit_aspect(x) = a + b*x + c*x**2 + d*x**3
# fit fit_aspect(x) "aspect.dat" using 1:2 via a,b,c,d

plot "aspect.dat" using 1:2:3:4:5:6 title "Transit data" lt 1 w xyerrorbars, \
    "aspect.dat" using 1:7 title "Transit fit" lw 2 lt 1 w lines smooth bezier, \
    "aspect.dat" using 1:8:9:10:11:12 title "Wing tip data" lt 2 w boxxyerror, \
    "aspect.dat" using 1:13 title "Wing tip fit" lw 2 lt 2 w lines smooth bezier

reset
