# set logscale x
set colorsequence classic
set grid
set title "Distance from t=0 and projected backward to v=0."
set xlabel "Video Time (s)"
set xtics
# set xrange [-33:-32]
#set format x ""

# set logscale y
set ylabel "Distance (m)"
set yrange [-1500:4000]
# set ytics 8,35,3
# set logscale y2
# set y2label "Bytes"
# set y2range [1:1e9]
# set y2tics

set pointsize 1
set datafile separator whitespace#"	"
set datafile missing "NaN"

set terminal svg size 700,500           # choose the file format

set output "distance.svg"   # choose the output device
#set key title "Window Length"
#  lw 2 pointsize 2

# Start distance arrows and labels
set arrow from -30.059,0 to -30.059,-787.468 lt 1
set arrow from -32.829,200 to -32.829,-949.243 lt 2
set arrow from -35.569,400 to -35.569,-1125.192 lt 3
set label "Calculated start at -30.1s, -787m" at -30.1,100 left font ",9"
set label "Calculated start at -32.8s, -949m" at -32.8,300 left font ",9"
set label "Calculated start at -35.6s, -1125m" at -35.6,500 left font ",9"
# End labels at start of take off
set arrow from 27.800,1000 to 27.800,1850 lt -1
set label "End asphalt 27.8s" at 27.8,900 center font ",10"
set arrow from 17.800,1915.392 to 27.800,1915.392 lt 1
set arrow from 17.800,2058.407 to 27.800,2058.407 lt 2
set arrow from 17.800,2201.423 to 27.800,2201.423 lt 3
set label "1915m" at 16.8,1915.4 right font ",10"
set label "2058m" at 16.8,2058.4 right font ",10"
set label "2201m" at 16.8,2201.4 right font ",10"
# End video
set arrow from 35.667,1500 to 35.667,2350 lt -1
set label "End video 35.7s" at 35.7,1400 center font ",10"
set arrow from 25.667,2609.259 to 35.667,2609.259 lt 1
set arrow from 25.667,2792.744 to 35.667,2792.744 lt 2
set arrow from 25.667,2976.229 to 35.667,2976.229 lt 3
set label "2609m" at 24.7,2609.3 right font ",10"
set label "2793m" at 24.7,2792.7 right font ",10"
set label "2976m" at 24.7,2976.2 right font ",10"

# linespoints
plot "distance.dat" using 1:2 title "-10 knots" lt 1 lw 0.5 w lines, \
    "distance.dat" using 1:3 title "Mid values" lt 2 lw 2 w lines, \
    "distance.dat" using 1:4 title "+10 knots" lt 3 lw 0.5 w lines
reset
