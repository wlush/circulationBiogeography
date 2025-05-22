import gc
import pandas as ps
import os
import sqlite3
import time

#reads in an sql file of particle tracks, subsets it by some criteria, and makes a smaller sql file

#directory where we can find outdata_run.sql
dataDir='output_trm/myCase/'

#filename to save subset of data in
outFile=dataDir+'even_subset.sql'

#check if small file exists. If so stop
assert not os.path.isfile(outFile),outFile+' exists. Delete if you wish and re-run script'

#open input and output sql file 
engineIn=sqlite3.connect(dataDir+'outdata_run.sql')
engineOut=sqlite3.connect(outFile)

#get some of the input data according to some selection criterion
#dataIn_iterator=ps.read_sql_query('select * from tracks where timeAfter < 30.0 and ny>1300 and ny<1500',
                                  #engineIn,chunksize=1000000)

dataIn_iterator = ps.read_sql_query('select * from tracks where trackID % 2.0 == 0.0 and (time*10.0) % 2.0 == 0.0',
                                    engineIn,chunksize = 1000000)
#loop over query, and write out
nchunk=0
for dataIn in dataIn_iterator:
    nchunk+=1
    print('dealing with chunk',nchunk)
    dataIn.to_sql('tracks',con=engineOut,index=False,if_exists='append')
    gc.collect()

print('done with transfering data, now making indices')
cursor=engineOut.cursor()
engineOut.commit()
    
#now add indices
cursor.execute('create index trackid_index on tracks(trackid)')
print('done trackid index')
cursor.execute('create index timeafter_index on tracks(timeafter)')
print('done timeafter index')
cursor.execute('create index time_index on tracks(time)')
print('done time index')
engineOut.commit()

jnk=os.stat(dataDir+'outdata_run.sql'); print('input file size',jnk.st_size/(1024**3),'Gb')
jnk=os.stat(outFile); print('output file size',jnk.st_size/(1024**3),'Gb')

engineOut.close()
engineIn.close()
