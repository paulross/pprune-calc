# set logscale x
set colorsequence classic
set grid
set title "Distance From Runway Start. From Figure 45 and 48."
set xlabel "Time From Threshold (s)"
set xtics
#set xrange [-5:60]
#set format x ""

# set logscale y
set ylabel "Error (m)"
#set yrange [:2000]
# set ytics 8,35,3
# set logscale y2
#set y2label "Difference (m)"
#set y2range [-6:3]
#set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

#set key title "Window Length"
set key right top
#  lw 2 pointsize 2

# Start distance arrows and labels
set arrow from 40,1653 to 55,1653 lt 1 nohead
set label "Runway end 1653m" at 47.5,1800 center font ",12"


#mid_error(t) = 200.0 + 1 * t * 2 * t**2 * 4 * t**3
mid_error(t) = 20.0 - 0.08 * t

# Polynomial for tile data: d (t) =  3.623e+00 +  8.862e+01 * t + -3.788e-01 * t**2 + -1.173e-02 * t**3 Value(0) =  3.623e+00
# Polynomial for tile data: d+(t) =  1.714e+01 +  8.675e+01 * t + -2.518e-01 * t**2 + -8.714e-03 * t**3 Value(0) =  1.714e+01
# Polynomial for tile data: d-(t) = -9.895e+00 +  9.049e+01 * t + -5.058e-01 * t**2 + -1.475e-02 * t**3 Value(0) = -9.895e+00
# Time range: 0.467 to 18.117 (s)
# Polynomial for slab data: v (t) =  9.110e+01 + -1.335e+00 * t +  6.935e-02 * t**2 + -4.952e-03 * t**3 Value(0) =  9.110e+01
# Integral polynomial: d(t) =  0.000e+00 +  9.110e+01 * t + -6.676e-01 * t**2 +  2.312e-02 * t**3 + -1.238e-03 * t**4
# Polynomial for slab data: v+(t) =  9.777e+01 + -3.379e+00 * t +  2.862e-01 * t**2 + -1.119e-02 * t**3 Value(0) =  9.777e+01
# Integral polynomial: d(t) =  0.000e+00 +  9.777e+01 * t + -1.690e+00 * t**2 +  9.542e-02 * t**3 + -2.797e-03 * t**4
# Polynomial for slab data: v-(t) =  8.444e+01 +  7.087e-01 * t + -1.475e-01 * t**2 +  1.284e-03 * t**3 Value(0) =  8.444e+01
# Integral polynomial: d(t) =  0.000e+00 +  8.444e+01 * t +  3.543e-01 * t**2 + -4.918e-02 * t**3 +  3.209e-04 * t**4

set terminal svg size 600,400           # choose the file format
set output "images/final_report_fig_45_and_48.svg"   # choose the output device

plot "data/final_report_fig_45.dat" using 1:8:9:10 title "Figure 45 (m)" w yerrorbars, \
    "data/final_report_fig_48.dat" using 1:8:9:10 title "Figure 48 (m)" w yerrorbars #, \
    "data/final_report_fig_48.dat" using 1:(mid_error($2)) title "Fitted to mid values" lw 2 w line

set terminal png size 600,400           # choose the file format
set output "images/final_report_fig_45_and_48.png"   # choose the output device

plot "data/final_report_fig_45.dat" using 1:8:9:10 title "Figure 45 (m)" w yerrorbars, \
    "data/final_report_fig_48.dat" using 1:8:9:10 title "Figure 48 (m)" w yerrorbars #, \
    "data/final_report_fig_48.dat" using 1:(mid_error($2)) title "Fitted to mid values" lw 2 w line

reset
