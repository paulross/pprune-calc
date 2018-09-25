# set logscale x
set grid
set title "Bearings to Observer\n(NOTE: Axes not to common scale)"
set xlabel "Distance from t=0 (m)"
set xrange [0:3000]
#set xrange [2200:2300]
set xtics
#set format x ""

# set logscale y
set ylabel "Offset to Observer (m)"
set yrange [200:-1000]
#set yrange [-750:-800]
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
#fit cost(x) "time_distance_bearing_with_yaw.dat" using 1:2 via a,b

set terminal svg size 1000,500           # choose the file format

set key off

set output "time_distance_bearing_with_yaw.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

y_base_value = 0

#set style line 1 lt 1 lw 2

set style line 1 lc rgb "blue" lw 0.5

#set style arrow 1 nohead ls 1

set arrow from 39,0 to 2880,-950 ls 4 nohead
set arrow from 83,0 to 2868,-950 ls 4 nohead
set arrow from 154,0 to 2848,-950 ls 4 nohead
set arrow from 174,0 to 2843,-950 ls 4 nohead
set arrow from 235,0 to 2826,-950 ls 4 nohead
set arrow from 297,0 to 2809,-950 ls 7 nohead
set arrow from 360,0 to 2791,-950 ls 7 nohead
set arrow from 410,0 to 2778,-950 ls 7 nohead
set arrow from 492,0 to 2755,-950 ls 7 nohead
set arrow from 559,0 to 2736,-950 ls 7 nohead
set arrow from 610,0 to 2722,-950 ls 7 nohead
set arrow from 770,0 to 2678,-950 ls 7 nohead
set arrow from 918,0 to 2638,-950 ls 7 nohead
set arrow from 1070,0 to 2596,-950 ls 7 nohead
set arrow from 1226,0 to 2553,-950 ls 6 nohead
set arrow from 1285,0 to 2537,-950 ls 6 nohead
set arrow from 1304,0 to 2531,-950 ls 6 nohead
set arrow from 1984,0 to 2344,-950 ls 14 nohead
set arrow from 2014,0 to 2336,-950 ls 14 nohead
set arrow from 2043,0 to 2328,-950 ls 14 nohead
set arrow from 2088,0 to 2315,-950 ls 14 nohead
set arrow from 2119,0 to 2307,-950 ls 14 nohead
set arrow from 2149,0 to 2299,-950 ls 14 nohead
set arrow from 2255,0 to 2269,-950 ls 14 nohead
set arrow from 2286,0 to 2261,-950 ls 14 nohead
set arrow from 2317,0 to 2252,-950 ls 14 nohead
set arrow from 2348,0 to 2244,-950 ls 14 nohead
set arrow from 2379,0 to 2235,-950 ls 14 nohead
set arrow from 2410,0 to 2227,-950 ls 14 nohead
set arrow from 2441,0 to 2218,-950 ls 14 nohead
set arrow from 2472,0 to 2210,-950 ls 14 nohead
set arrow from 2500,0 to 2202,-950 ls 14 nohead
set arrow from 2535,0 to 2192,-950 ls 14 nohead
set arrow from 2566,0 to 2184,-950 ls 14 nohead
set arrow from 2595,0 to 2176,-950 ls 14 nohead
set arrow from 1791,-745 to 2266,-745 lw 3
set label 1 "t=0.7" at 39,20 right rotate by 60 font ",9"
set label 2 "t=1.5" at 83,20 right rotate by 60 font ",9"
set label 3 "t=2.7" at 154,20 right rotate by 60 font ",9"
set label 4 "t=3.0" at 174,20 right rotate by 60 font ",9"
set label 5 "t=4.0" at 235,20 right rotate by 60 font ",9"
set label 6 "t=5.0" at 297,20 right rotate by 60 font ",9"
set label 7 "t=6.0" at 360,20 right rotate by 60 font ",9"
set label 8 "t=6.8" at 410,20 right rotate by 60 font ",9"
set label 9 "t=8.0" at 492,20 right rotate by 60 font ",9"
set label 10 "t=9.0" at 559,20 right rotate by 60 font ",9"
set label 11 "t=9.7" at 610,20 right rotate by 60 font ",9"
set label 12 "t=12.0" at 770,20 right rotate by 60 font ",9"
set label 13 "t=14.0" at 918,20 right rotate by 60 font ",9"
set label 14 "t=16.0" at 1070,20 right rotate by 60 font ",9"
set label 15 "t=18.0" at 1226,20 right rotate by 60 font ",9"
set label 16 "t=18.7" at 1285,20 right rotate by 60 font ",9"
set label 17 "t=19.0" at 1304,20 right rotate by 60 font ",9"
set label 18 "t=27.0" at 1984,20 right rotate by 60 font ",9"
set label 19 "t=27.3" at 2014,20 right rotate by 60 font ",9"
set label 20 "t=27.6" at 2043,20 right rotate by 60 font ",9"
set label 21 "t=28.1" at 2088,20 right rotate by 60 font ",9"
set label 22 "t=28.5" at 2119,20 right rotate by 60 font ",9"
set label 23 "t=28.8" at 2149,20 right rotate by 60 font ",9"
set label 24 "t=30.0" at 2255,20 right rotate by 60 font ",9"
set label 25 "t=30.3" at 2286,20 right rotate by 60 font ",9"
set label 26 "t=30.6" at 2317,20 right rotate by 60 font ",9"
set label 27 "t=31.0" at 2348,20 right rotate by 60 font ",9"
set label 28 "t=31.3" at 2379,20 right rotate by 60 font ",9"
set label 29 "t=31.6" at 2410,20 right rotate by 60 font ",9"
set label 30 "t=32.0" at 2441,20 right rotate by 60 font ",9"
set label 31 "t=32.3" at 2472,20 right rotate by 60 font ",9"
set label 32 "t=32.6" at 2500,20 right rotate by 60 font ",9"
set label 33 "t=33.0" at 2535,20 right rotate by 60 font ",9"
set label 34 "t=33.3" at 2566,20 right rotate by 60 font ",9"
set label 35 "t=33.6" at 2595,20 right rotate by 60 font ",9"
set label "Observer assumed at x=2266, y=-745" at 1766,-745 right font ",14"

plot "time_distance_bearing_with_yaw.dat" using 2:(y_base_value)
reset
