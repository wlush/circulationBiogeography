#created 1/7/19 by wgl - modified 1/8/19
#Based on simplePCM.py in Analysis (simplified for simplified SQL files)
#Creates a partial connectivity matrix (for shorter runs) to be combined into
#larger connectivity matrices (for subsetting larger runs)

#Implementation for BIG sql files

import time
import os
import datetime as dt
import matplotlib.dates as mdt
import numpy as np
import pylab as p
import pandas as pd
import netCDF4 as nc
import scipy.spatial as sp
import scipy.sparse as sparse
import sqlite3

#NOTE - OUTPUT IS MEANT TO BE PART OF LARGER CONNECTIVITY MATRIX
#case = 'Atlantic'
#case = 'norPac'
#case = 'souPac'
#case = 'fulInd'
case = 'indPac'
year = '2017'
month = ['01','02','03','04','05','06','07','08','09','10','11','12']

print(case, year)

#Set PLD and competency period (in days):
PLD = 45 #30 #3  #15
compPer = 20 #1  #6
setSt = PLD-compPer

#if output directory exists, put files into it, otherwise don't

outputDirPath = '/data/guppy/willlush/conn_matrices/cGrid/'+case+'/'
outputDirName = case+year+'_PLD'+str(PLD)+'_c'+str(compPer)+'_PCM/'

assert True, 'CAUTION: BIG CHUNKS'

if True:
    if os.path.isdir(outputDirPath+outputDirName):
        print('directory exists!')
        outPath = outputDirPath+outputDirName
    else:
        print('creating new directory')
        outPath = outputDirPath+outputDirName
        os.mkdir(outPath)

for mo in month:
    #Directory where sql database file exists
    dataDir = '../Runs/'+case+'/'+year+'/'+case+'_'+year+'_'+mo+'/output_trm/myCase/'
    dataDir = '/data/bigNFS/willlush/tracmassTrajectories_coastalCompressed/'+case+'/'+year+'/'+case+'_'+year+'_'+mo+'/output_trm/myCase/'
    if case == 'Atlantic':
        dataDir = '/data/guppy2/willlush/trm/saveSpace/Atlantic/'+year+'/'+case+'_'+year+'_'+mo+'/output_trm/myCase/'
    assert True, 'dataDir is:'+dataDir

    #connect to sqlite file
    #engine=sqlite3.connect(dataDir+'outdata_run.sql')
    engine=sqlite3.connect(dataDir+'connectivity.sql')

    #Get month of partial connectivity matrix
    stDay = np.amin(pd.read_sql_query('select GCMdate from starts',engine).values)
    stMo = mdt.num2date(stDay).month
    stYr = mdt.num2date(stDay).year
    #check against filename to make sure all is good date-wise
    assert int(mo) == stMo, 'Mismatch in months, something is VERY wrong'
    assert int(year) == stYr, 'Mismatch in years, something is VERY wrong'

    #make set of start dates for the month:
    sday = dt.timedelta(days=1)
    sdate1 = dt.date(stYr, stMo, 1)
    sdates = []
    sd = sdate1
    while sd.month == stMo:
        sdates.append(sd)
        sd += sday
        
    stDates = set(np.array(mdt.date2num(sdates)).astype(int))

    #---------------------------------------------------------------------------

    #create dict of particle IDs and start locations as tags:
    stLocs = pd.read_sql_query('select ntrac, nx, ny from starts where GCMdate <= %f'%(max(stDates)),engine)
    stLocs['tags'] = stLocs['nx']*10000+stLocs['ny']
    #sort tag location west to east and north to south 
    stLocs = stLocs.sort_values(by = ['tags'])

    #dictionary of start locations
    stDict = dict(zip(stLocs['ntrac'].values,stLocs['tags'].values))

    #---------------------------------------------------------------------------
    #create connectivity matrix and related tools - ij2tag; tag2ij; relCount
    
    #create ij2tag array - for use with connectivity matrix
    ij2tag = np.unique(stLocs['tags'].values)

    #tag2ij - goes from tags to an i,j location in the cm
    tag2ij = dict.fromkeys(ij2tag)
    for key in tag2ij.keys():
        tag2ij[key] = list(np.where(ij2tag==key)[0])[0]

    #creates an empty connectivity matrix
    cmLength = len(ij2tag)
    cm = np.zeros((cmLength,cmLength))
    #creates a vector for number of larvae released from each location in cm
    relCount = np.zeros(cmLength) #counts particles released from given box
    print('empty connectivity matrix created')

    #---------------------------------------------------------------------------

    #!!!!! tAfter is 10 times fractional days since release !!!!

    #the chunkening:
    print('populating connectivity matrix for %s'%(mo))
    chunk = 1000000
    chunkMin = 0
    maxID = max(stDict.keys())

    while chunkMin < maxID:
        #find when particles enter coastal waters during their competency periods
        print (chunkMin, maxID)
        setLocs = pd.read_sql_query('select ntrac, nx, ny, tAfter from tracks where (tAfter between %f and %f) and (ntrac between %f and %f)'%(setSt*10,PLD*10,chunkMin,chunkMin+chunk),engine)

        #sort settlement locations - ensures that the chronological first coastal
        #value is indeed the first in the dataframe
        setLocs.sort_values('tAfter',inplace=True)
        #drop all duplicate particle IDs, keeping the first value - the larvae
        #'settles' in the first coastal grid box it encounters during the
        #competency period
        setLocs.drop_duplicates('ntrac',inplace=True,keep='first')

        setLocs['tags'] = setLocs['nx']*10000+setLocs['ny']
        setDict = dict(zip(setLocs['ntrac'].values,setLocs['tags'].values))

        for ID in stDict.keys():
            ijSt = tag2ij[stDict[ID]]
            relCount[ijSt]+=1
            if ID in setDict.keys():
                ijEnd = tag2ij[setDict[ID]]
                cm[ijEnd,ijSt]+=1

        chunkMin += chunk

    if False:
        p.figure(1)
        p.clf()
        p.imshow(np.log(cm))
        p.colorbar()
        p.show()
        
    if True:
        outFileName = case+year+'_'+mo+'_PLD'+str(PLD)+'_c'+str(compPer)+'_PCM'
        out = outPath+outFileName
        cms = sparse.csr_matrix(cm,dtype=np.int16)
        np.savez(out,
                 cm = cms,
                 ij2tag = ij2tag,
                 tag2ij = tag2ij,
                 relCount = relCount)
