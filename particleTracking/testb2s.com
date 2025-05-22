#!/bin/bash

#begin by opening directories and running

#case name
#casename='Atlantic'
#casename='norPac'
#casename='souPac'
#casename='indPac'
#casename='fulInd'
casename='testTiming'

#set year
yr=2012

#number of months over which to run - run in chunks of 3 on delta
#mo='01 02 03 04 05 06 07 08 09 10 11 12'
mo='01'

for i in $mo 
do
    STR=$casename'_'$yr'_'$i
    cd ./Runs/${casename}/${yr}/${STR}
    
    echo $i &
    
    cd ../../../../
    cd ./Analysis/

    python bash2SQL.py $i $yr &


    cd ../
    
done
