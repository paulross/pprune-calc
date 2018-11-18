# set logscale x
set colorsequence classic
set grid
set title "Bearings to Observer\n(NOTE: Axes not to common scale)"
set xlabel "Distance from runway start (m)"
set xrange [1000:4000]
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

set arrow from 1221,0 to 3935,-950 ls 4 nohead
set arrow from 1265,0 to 3925,-950 ls 4 nohead
set arrow from 1335,0 to 3909,-950 ls 4 nohead
set arrow from 1355,0 to 3904,-950 ls 4 nohead
set arrow from 1416,0 to 3891,-950 ls 4 nohead
set arrow from 1478,0 to 3877,-950 ls 7 nohead
set arrow from 1542,0 to 3862,-950 ls 7 nohead
set arrow from 1592,0 to 3851,-950 ls 7 nohead
set arrow from 1673,0 to 3832,-950 ls 7 nohead
set arrow from 1741,0 to 3817,-950 ls 7 nohead
set arrow from 1792,0 to 3806,-950 ls 7 nohead
set arrow from 1952,0 to 3769,-950 ls 7 nohead
set arrow from 2099,0 to 3736,-950 ls 7 nohead
set arrow from 2251,0 to 3702,-950 ls 7 nohead
set arrow from 2408,0 to 3666,-950 ls 6 nohead
set arrow from 2467,0 to 3653,-950 ls 6 nohead
set arrow from 2485,0 to 3649,-950 ls 6 nohead
set arrow from 3165,0 to 3495,-950 ls 14 nohead
set arrow from 3195,0 to 3488,-950 ls 14 nohead
set arrow from 3225,0 to 3481,-950 ls 14 nohead
set arrow from 3270,0 to 3471,-950 ls 14 nohead
set arrow from 3300,0 to 3464,-950 ls 14 nohead
set arrow from 3330,0 to 3457,-950 ls 14 nohead
set arrow from 3437,0 to 3433,-950 ls 14 nohead
set arrow from 3468,0 to 3426,-950 ls 14 nohead
set arrow from 3498,0 to 3419,-950 ls 14 nohead
set arrow from 3529,0 to 3412,-950 ls 14 nohead
set arrow from 3560,0 to 3405,-950 ls 14 nohead
set arrow from 3591,0 to 3398,-950 ls 14 nohead
set arrow from 3622,0 to 3391,-950 ls 14 nohead
set arrow from 3654,0 to 3384,-950 ls 14 nohead
set arrow from 3682,0 to 3378,-950 ls 14 nohead
set arrow from 3716,0 to 3370,-950 ls 14 nohead
set arrow from 3748,0 to 3363,-950 ls 14 nohead
set arrow from 3776,0 to 3356,-950 ls 14 nohead
set arrow from 2959,-775 to 3434,-775 lw 3
set label 1 "t=0.7" at 1221,20 right rotate by 60 font ",9"
set label 2 "t=1.5" at 1265,20 right rotate by 60 font ",9"
set label 3 "t=2.7" at 1335,20 right rotate by 60 font ",9"
set label 4 "t=3.0" at 1355,20 right rotate by 60 font ",9"
set label 5 "t=4.0" at 1416,20 right rotate by 60 font ",9"
set label 6 "t=5.0" at 1478,20 right rotate by 60 font ",9"
set label 7 "t=6.0" at 1542,20 right rotate by 60 font ",9"
set label 8 "t=6.8" at 1592,20 right rotate by 60 font ",9"
set label 9 "t=8.0" at 1673,20 right rotate by 60 font ",9"
set label 10 "t=9.0" at 1741,20 right rotate by 60 font ",9"
set label 11 "t=9.7" at 1792,20 right rotate by 60 font ",9"
set label 12 "t=12.0" at 1952,20 right rotate by 60 font ",9"
set label 13 "t=14.0" at 2099,20 right rotate by 60 font ",9"
set label 14 "t=16.0" at 2251,20 right rotate by 60 font ",9"
set label 15 "t=18.0" at 2408,20 right rotate by 60 font ",9"
set label 16 "t=18.7" at 2467,20 right rotate by 60 font ",9"
set label 17 "t=19.0" at 2485,20 right rotate by 60 font ",9"
set label 18 "t=27.0" at 3165,20 right rotate by 60 font ",9"
set label 19 "t=27.3" at 3195,20 right rotate by 60 font ",9"
set label 20 "t=27.6" at 3225,20 right rotate by 60 font ",9"
set label 21 "t=28.1" at 3270,20 right rotate by 60 font ",9"
set label 22 "t=28.5" at 3300,20 right rotate by 60 font ",9"
set label 23 "t=28.8" at 3330,20 right rotate by 60 font ",9"
set label 24 "t=30.0" at 3437,20 right rotate by 60 font ",9"
set label 25 "t=30.3" at 3468,20 right rotate by 60 font ",9"
set label 26 "t=30.6" at 3498,20 right rotate by 60 font ",9"
set label 27 "t=31.0" at 3529,20 right rotate by 60 font ",9"
set label 28 "t=31.3" at 3560,20 right rotate by 60 font ",9"
set label 29 "t=31.6" at 3591,20 right rotate by 60 font ",9"
set label 30 "t=32.0" at 3622,20 right rotate by 60 font ",9"
set label 31 "t=32.3" at 3654,20 right rotate by 60 font ",9"
set label 32 "t=32.6" at 3682,20 right rotate by 60 font ",9"
set label 33 "t=33.0" at 3716,20 right rotate by 60 font ",9"
set label 34 "t=33.3" at 3748,20 right rotate by 60 font ",9"
set label 35 "t=33.6" at 3776,20 right rotate by 60 font ",9"
set label "Observer assumed at x=3434, y=-775" at 2934,-775 right font ",14"

plot "time_distance_bearing_with_yaw.dat" using 2:(y_base_value)
reset
