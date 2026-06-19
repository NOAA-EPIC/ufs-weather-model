#!/bin/bash

#========================================================
. "${LMOD_ROOT}"/lmod/init/bash
module load grads

# if color bar script is not present, get it from github:
[[ -f cbar.gs ]] || wget -q https://raw.githubusercontent.com/NOAA-EPIC/Aquaplanet/refs/heads/main/utils/cbar.gs

cat << EOF > plot.j
*----------------------------------------------
reinit
set gxout shaded
set display color white
c
sdfopen orig-results-000/atmf2184.nc
sdfopen orig-results-002/atmf2184.nc

*----------------------------------------------
* UGRD
*----------------------------------------------
set z 73
set grads off
set clevs -5 0 5 10 15 20 30 40
d ugrd.1
run cbar.gs
draw title Jet stream (control)
printim jet-control.png x1200 y1000
c

set grads off
set clevs -5 0 5 10 15 20 30 40
d ugrd.2
run cbar.gs
draw title Jet stream (test 2)
printim jet-test2.png x1200 y1000
c

set grads off
set clevs -2 -1 -0.5 -0.2 0.2 0.5 1 2
d ugrd.2-ugrd.1
run cbar.gs
draw title Jet stream diff (test 2 - control)
printim jet-diff-test2.png x1200 y1000
c
*----------------------------------------------

*----------------------------------------------
* TEMP
*----------------------------------------------
set z 49
set grads off
set clevs -25 -20 -15 -10 -5 0 5
d tmp.1-273
run cbar.gs
draw title Temp 500hPa (control)
printim tmp-control.png x1200 y1000
c

set grads off
set clevs -25 -20 -15 -10 -5 0 5
d tmp.2-273
run cbar.gs
draw title Temp 500hPa (test 2)
printim tmp-test2.png x1200 y1000
c

set grads off
set clevs -1 -0.5 -0.2 -0.1 0.1 0.2 0.5 1
d tmp.2-tmp.1
run cbar.gs
draw title Temp 500hPa diff (test 2 - control)
printim tmp-diff-test2.png x1200 y1000
c
*----------------------------------------------

*----------------------------------------------
*precip
*----------------------------------------------
reinit
set gxout shaded
set display color white
c
sdfopen orig-results-000/sfcf2184.nc
sdfopen orig-results-002/sfcf2184.nc
*----------------------------------------------
set rgb 40 128 0 160
set rgb 42 128 0 208
set rgb 44 128 0 255
set rgb 46 96 0 224
set rgb 48 0 0 192
set rgb 50 0 88 208
set rgb 52 0 144 224
set rgb 54 0 200 240
set rgb 56 0 255 255
set rgb 58 128 255 64
set rgb 60 192 255 0

set grads off
set clevs 0 1 2 3 4 5 6 7 8 9
set ccols 60 58 56 54 52 50 48 46 44 42 40
d prate_ave.1*86400
run cbar.gs
draw title Precip mm/day (control)
printim prec-control.png x1200 y1000
c

set grads off
set clevs 0 1 2 3 4 5 6 7 8 9
set ccols 60 58 56 54 52 50 48 46 44 42 40
d prate_ave.2*86400
run cbar.gs
draw title Precip mm/day (test 2)
printim prec-test2.png x1200 y1000
c

set grads off
set clevs -0.05 -0.02 -0.01 -0.005 0.005 0.01 0.02 0.05
d prate_ave.2*86400-prate_ave.1*86400
run cbar.gs
draw title Precip mm/day (test 2 - control)
printim prec-diff-test2.png x1200 y1000
c

EOF
#========================================================
echo \'exec plot.j\'       > plot.gs
echo \'quit\'             >> plot.gs
grads -blc "run plot.gs" > /dev/null 2>&1
#========================================================

#========================================================
#--- clean:
rm -f plot.j plot.gs
#========================================================
