# set logscale x
set grid
set title "Angle of View."
set xlabel "Video Time (s)"
set mxtics 5
#set xrange [0:3000]
#set xtics
#set format x ""

# set logscale y
set ylabel "Angle (degrees)"
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
#fit cost(x) "angle_of_view.dat" using 1:2 via a,b

set terminal svg size 1000,500           # choose the file format

# set key off

set output "angle_of_view.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# fit_aspect(x) = a + b*x + c*x**2 + d*x**3
# fit fit_aspect(x) "angle_of_view.dat" using 1:2 via a,b,c,d

plot "angle_of_view.dat" using 1:2:3:4:5:6 title "Horizontal View" lt 1 w xyerrorbars, \
    "angle_of_view.dat" using 1:7 title "Horizontal View fit" lw 2 lt 1 w lines smooth bezier, \
    "angle_of_view.dat" using 1:8:9:10:11:12 title "Vertical View" lt 2 w boxxyerror, \
    "angle_of_view.dat" using 1:13 title "Vertical View fit" lw 2 lt 2 w lines smooth bezier

reset
