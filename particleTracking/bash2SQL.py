#from simpleSQL.py - streamlined SQLite3 files for big (basin-scale) tracmass
#runs - changed to accept command-line args
#created 12/18/2018 wgl

from pylab import *
from numpy import *
import numpy as np
import netCDF4 as nc
import pandas as ps
import gzip
import os
import gc
from collections import defaultdict
import sqlite3
import time
import subprocess as sbp
import sys

#reads in binary trajectories and simplifies them into days and gridboxes

#case = 'ECNA'
#case ='Atlantic'
#case = 'norPac'
#case='souPac'
#case='indPac'
#case='fulInd'
case='testTiming'

#seedfile locations
sFileLoc = '/Runs/seedfiles/'
sFile = case+'.seed'

#year = '2008'
clIn = sys.argv
print(clIn)
mo = clIn[1]
year = clIn[2]
print(mo, year)


#dataDir = '../Runs/ECNA/'+year+'/ECNA_'+year+'_'+mo+'/output_trm/myCase/'
dd = '/data/guppy/willlush/trm_big_runs/cGrid'
dataDir = dd+'/Runs/'+case+'/'+year+'/'+case+'_'+year+'_'+mo+'/output_trm/myCase/'
print(dataDir)
assert True
#if .bin file is zipped, unzip
if True:
    #check if netcdf data file outdata_run.nc exists
    if os.path.isfile(dataDir+'outdata_run.sql'):
        print('outdata_run.sql file exists!')
        engine=sqlite3.connect(dataDir+'outdata_run.sql')
        if os.path.isfile(dataDir+'connectivity.sql'):
            print('connectivity.sql file exists!')
        print('   Done reading sql file')
    else:
        #open and read file into pandas dataframe
        print('reading file in and writing to sql')
        engine=sqlite3.connect(dataDir+'outdata_run.sql')
        prop=sqlite3.connect(dataDir+'connectivity.sql')

        dtRun = np.dtype([('ntrac', np.int32), ('GCMdate',np.int32),
                          ('nx',np.float32),('ny',np.float32),
                          ('nzInvert',np.float32),('fracDay',np.float64)])
        #number of bytes - 4+4+4+4+4+8 = 28 bytes per entry
        dtini =  np.dtype([('ntrac', np.int32), ('GCMdate',np.int32),
                           ('nx',np.float32),('ny',np.float32),
                           ('nzInvert',np.float32)])

        #get number of entries (for chunking)
        # should be 28 bytes per entry for run file
        fileSizeRun = os.stat(dataDir + 'outdata_run.bin').st_size
        entrySizeRun = fileSizeRun/28 #divided by 28 bytes

        #should be 20 bytes per entry for ini file
        fileSizeini = os.stat(dataDir + 'outdata_ini.bin').st_size
        entrySizeini = fileSizeini/20 #divided by 20 bytes (size of ini entry)

        #chunksize of 1000000 points
        chunkSize = 10000000
        nChunksRun = int(np.ceil(entrySizeRun/chunkSize))
        nChunksini = int(np.ceil(entrySizeini/chunkSize))

        #input file
        fid = open(dataDir + 'outdata_run.bin','r')
        initin = open(dataDir + 'outdata_ini.bin','r')

        #make 'starts' in sql file
        for n in np.arange(nChunksini):
            ichunk = ps.DataFrame(np.fromfile(initin,dtype = dtini,
                                              count = chunkSize))
            ichunk['nx'] = np.floor(ichunk['nx']).astype(np.int)
            ichunk['ny'] = np.floor(ichunk['ny']).astype(np.int)
            ichunk.to_sql('starts',con=engine,index=False,if_exists='append')
            ichunk.to_sql('starts',con=prop,index=False,if_exists='append')

        print('done creating starts')

        #make dicts of start values for quick access and save
        IDst = ps.read_sql_query('select ntrac,GCMdate,nx,ny from starts',
                                 engine)
        stTups = set(zip(IDst['nx'].values,IDst['ny'].values))
        daySt = dict(zip(IDst['ntrac'].values,IDst['GCMdate'].values)) #dict linking ntracs and start dates

        #testing
        if False:
            nChunksRun = 1

        print('number of chunks: %s'%(nChunksRun))

        #make 'tracks' in sql file
        for n in np.arange(nChunksRun):
            chunk = ps.DataFrame(np.fromfile(fid,dtype = dtRun,count = chunkSize ))
            chunk['nx'] = np.floor(chunk['nx']).astype(np.int)
            chunk['ny'] = np.floor(chunk['ny']).astype(np.int)
            #36 would be above water surface...
            chunk['nzInvert'] = np.floor(chunk['nzInvert']).astype(np.int)

            #make tAfter column:
            IDarr = chunk['ntrac'].values
            SDarr = np.array([daySt[ID] for ID in IDarr])
            #multiplied by 10 to have sortable value but reduce size
            #tAfter is 10 times fractional days since release 
            chunk['tAfter'] = np.floor((chunk['fracDay']-SDarr)*10).astype(np.int)
            chunk.drop('fracDay',axis = 1,inplace = True)
            chunk = chunk.drop_duplicates(['ntrac','nx','ny','GCMdate'])
            testCoast = tuple(zip(chunk['nx'],chunk['ny']))
            tested = [tup in stTups for tup in testCoast]
            chunk['coastal'] = tested

            chunk.to_sql('tracks',con=engine,index=False,if_exists='append')
            print('done writing chunk to oudata_run.sql')

            #make connectivity sql file - use only coastal points
            conChunk = chunk[chunk['coastal']==True]
            conChunk = conChunk.drop(['GCMdate','coastal'],axis=1)
            conChunk.to_sql('tracks',con=prop,index=False,if_exists='append')
            print('done writing chunk to connectivity.sql')
            print('case: '+case+' year: '+year+' month: '+mo)

            print('                       done with chunk %s'%(n))
            gc.collect()

        print('done creating tracks')

        fid.close()
        initin.close()

        #*******************************************************************

        print('done creating sql, create outdata_run.sql indices')
        cursor=engine.cursor()
        engine.commit()

        #now do testing of access time
        #for shits and giggles, read one track and time
        tic=time.time()
        cursor.execute('select * from tracks where ntrac = ?',(55,))
        jnk=cursor.fetchall()
        print('found records  ',len(jnk),'for one track in',time.time()-tic,'seconds')


        #print size
        jnk=os.stat(dataDir+'outdata_run.sql'); print('File size is',jnk.st_size/(1024**3))

        #now add indices

        cursor.execute('create index ntrac_index on tracks(ntrac)')
        engine.commit()
        jnk=os.stat(dataDir+'outdata_run.sql'); print('File size is (ntrac index)',jnk.st_size/(1024**3))

        cursor.execute('create index tAfter_index on tracks(tAfter)')
        engine.commit()
        jnk=os.stat(dataDir+'outdata_run.sql'); print('File size is (tAfter index)',jnk.st_size/(1024**3))

        cursor.execute('create index coastal_index on tracks(coastal)')
        engine.commit()
        jnk=os.stat(dataDir+'outdata_run.sql'); print('File size is (2 index)',jnk.st_size/(1024**3))

        cursor.execute('create index ntracIndex on starts(ntrac)')
        engine.commit()
        jnk=os.stat(dataDir+'outdata_run.sql'); print('File size is (3 index)',jnk.st_size/(1024**3))

        cursor.execute('create index GCMdateIndex on starts(GCMdate)')
        engine.commit()
        jnk=os.stat(dataDir+'outdata_run.sql'); print('File size is (4 index)',jnk.st_size/(1024**3))

        print(' ')
        print('ok, all done, close outdata_run.sql')
        print('case: '+case+' year: '+year+' month: '+mo)
        print(' ')
        #*******************************************************************

        print('create connectivity.sql indices')
        cursor=prop.cursor()
        prop.commit()

        #now do testing of access time
        #for shits and giggles, read one track and time
        tic=time.time()
        prop.execute('select * from tracks where ntrac = ?',(55,))
        jnk=cursor.fetchall()
        print('found records  ',len(jnk),'for one track in',time.time()-tic,'seconds')


        #print size
        jnk=os.stat(dataDir+'connectivity.sql'); print('File size is',jnk.st_size/(1024**3))

        #now add indices
        cursor.execute('create index ntrac_index on tracks(ntrac)')
        prop.commit()
        jnk=os.stat(dataDir+'connectivity.sql'); print('File size is (ntrac index)',jnk.st_size/(1024**3))

        cursor.execute('create index tAfter_index on tracks(tAfter)')
        prop.commit()
        jnk=os.stat(dataDir+'connectivity.sql'); print('File size is (tAfter index)',jnk.st_size/(1024**3))

        cursor.execute('create index ntracIndex on starts(ntrac)')
        prop.commit()
        jnk=os.stat(dataDir+'connectivity.sql'); print('File size is (3 index)',jnk.st_size/(1024**3))

        cursor.execute('create index GCMdateIndex on starts(GCMdate)')
        prop.commit()
        jnk=os.stat(dataDir+'connectivity.sql'); print('File size is (4 index)',jnk.st_size/(1024**3))

        print(' ')
        print('ok, all done, close connectivity.sql')
        print('case: '+case+' year: '+year+' month: '+mo)
        print(' ')

        engine.close()
        prop.close()

        sbp.check_call(['gzip', dataDir+'outdata_run.sql'])
