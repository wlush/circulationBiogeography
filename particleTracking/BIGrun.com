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
#mo='01 02 03 04' # 09 10 11 12'
#mo='05 06 07 08'
#mo='09 10 11 12'
mo='01'

for i in $mo 
do
    STR=$casename'_'$yr'_'$i
    cd ./Runs/${casename}/${yr}/${STR}

    #remove executable and rebuild
    /bin/rm runtrm
    make clean
    make 

    time ./runtrm | tee run_log.txt &
    
    cd ../../../../
    
done

echo Done with tracmass runs, make sql files!


