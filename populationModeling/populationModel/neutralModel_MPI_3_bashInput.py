#code to run using MPI: mpiexec -n 16 python neutralModel_MPI_3_excludePoints.py

import numpy as np
import pylab as p
import netCDF4 as nc
import pandas as pd
import sklearn.preprocessing as skp
import time
import sys
#import multiprocessing
import xarray as xr
import os

runMPI=True #try to make it so code works if true or if false!
if runMPI:
    from mpi4py import MPI
    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    size=comm.Get_size()
    print('Starting rank ',rank,' of ',size,flush=True)
else:
    rank=0
    size=1

#what type do we run the model with? Make a numpy type
popMatType=np.float64
popMatType=np.float32

#======================================================================
#configure model run, and when and where to save data

#LOADING DATA AND PARAMETERS
#load parameters - this is for the South Pacific, which should run reasonably fast
if False:
    assert False
    #medium size run, about twice as big
    case = 'souPac' #which analysis region
    pld = 30  #pld
    cPer = 10 #accompanying competence period
    season = 'spr' #northern hemisphere season
else:
    case = sys.argv[1]
    season = sys.argv[2]
    pld = int(sys.argv[3])
    cPer = int(sys.argv[4])

    #print(type(case), type(pld), type(cPer), pld, cPer)
    assert True

#how long to run
#WHEN AND WHERE TO SAVE
saveDir = '/data/guppy/willlush/neutralModelMPI_output/'
outDir=saveDir+'chunks_%s_data_season_%s_PLD%0.0d_cPer%0.0d/'%(case,season,pld,cPer)
nGenMax=1000 #this is the actual number of generations to run (not +1 number of generations)
#saveInterval=10
#whenSave=np.arange(0,nGenMax+1,saveInterval) #list of generations to save
wsList = [0,1,2,3,4,5,10,25,50,75,100,250,500,750,999,1000]
whenSave = np.array(wsList)

print(case,pld,season)

#======================================================================
#the following code loads all the data, and is the same for all
#ranks. Remember that all ranks need the entire connectivity matrix,
#though since that is a sparse matrix, this should not be a big deal

# make directory to save data in -- but only if rank 0 !!!!!!!!!!!!!!!!
if rank==0:
    try:
        os.mkdir(outDir)
    except FileExistsError:
        print('If out want to write over ',outDir,'you must remove it manually')
        assert False, 'Lets not write over expensive data'

dDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'
#import sys
#sys.path.insert(0, dDir) #import modules from /Popmodel directory CJMP prefers files local for doing this
import tagToLoc as ttl
import fixOffByOne as fob


tic=time.time()
#load landmask, ij2tag
testname = '/data/guppy2/willlush/Mercator/cGrid/trmSymlinks/Mask.nc'
lm = nc.Dataset(testname,'r')
tM = lm['tmask'][0,0,:,:].data.astype(bool) #landmask (plotting)
lat = lm["nav_lat"][:].data
lon = lm["nav_lon"][:].data
lm.close()

#grid tags/connectivity matrix locations
asdName = dDir+'/ASdict%s.npz'%(case)
asdOpen = np.load(asdName)
ij2tag = asdOpen['ij2tag'] #conn matrix location to grid location
asdOpen.close()
ijx,ijy = ttl.tagArr2locs(fob.fixTags(ij2tag)) #grid xy (plotting)
lonVec = lon[ijy, ijx]+0
latVec = lat[ijy, ijx]+0

del lon
del lat

#load regional locations, sorted by distance
#cjmp right directory?
loadMat = np.load('/data/guppy/willlush/trm_big_runs/cGrid/Analysis/newModel_allSpecies/distanceSort/distanceSort_noIslands_%s.npz'%(case))
sortM = loadMat['sortTT']
loadMat.close()
region = sortM

#now put lonVec and latVec in order as defined by region
lonVec=lonVec[region]
latVec=latVec[region]


#load points to remove
getPoints = np.load('../indoPacific_removePoints.npz')
loadLat = getPoints['latVec']
loadLon = getPoints['lonVec']

bMask = np.zeros(len(lonVec))
for ix in np.arange(len(loadLat)):
    ind = np.argwhere((lonVec==loadLon[ix])&(latVec==loadLat[ix]))
    bMask[ind]=1
#################

# load connectivity matrix:
bigDir = '/data/guppy/willlush/conn_matrices/cGrid/%s/'%(case)
cDir = '/comb%s_PLD%s_c%s/'%(case,pld,cPer)
mName = '%s_%s_%s_%s.npz'%(case,season,pld,cPer)
data = np.load(bigDir+cDir+mName, allow_pickle=True)
cm = data['cm'].item().astype(np.float32).tolil()
data.close()
cm_size = cm.shape[0]

#in general, only print from rank 0
if rank==0:
    print('done loading data in',time.time()-tic,flush=True)

tic=time.time()
#SUBSETTING CONNECTIVITY MATRIX/CREATING INITIAL POPULATION
#IMPORTANT STEP - correctly subsets and orders the connectivity matrix
#subsetCM is the connectivity matrix
#
#this time step is time consuming, and memory consuming. So lets only
#do it at rank 0 and send the results to the rest of the code. This
#saves LOTS of memory on startup, because of the big ijX, ijY grids,
#which are full!
#
#if fastRun is true, save subsetCM to rerun with different param quickly.
#do not keep this on, only for debugging

#fastRun=True ; isFirst=True #first run for debugging
#fastRun=True ; isFirst=False #subsequent runs for debugging
fastRun=False #what should be true for production runs. 

if not fastRun:
    isFirst=True
if rank==0:
    if isFirst :
        ijX,ijY = np.meshgrid(region,region)
        global subsetCM 
        subsetCM = cm[ijX,ijY].tocsr()

        del cm
        del ijX
        del ijY

        if fastRun:
            print('HACK! SAVING subsetCM',flush=True)
            np.savez('jnk.npz',subsetCM=subsetCM)

    if fastRun and (not isFirst):
        print('HACK! LOADING PRECOMPUTED subsetCM',flush=True)
        jnk=np.load('jnk.npz',allow_pickle=True)
        subsetCM=jnk['subsetCM'][()]
        del jnk
        
    if False:
        print('HORIBLE HACK, TRANSPOSE subsetCM',type(subsetCM),flush=True)
        subsetCM=subsetCM.transpose()
        print('   done with HORIBLE HACK, TRANSPOSE subsetCM',type(subsetCM),flush=True)

else:
    subsetCM=[] #so that it is initialized in the call below for ranks other than 0

#now broadast subsetCM to other codes note that we use the lower case
#"bcast" which handles python objects, not the upper case one, which
#only does memory buffers (and is much quicker). A good reference of
#all this is
#https://rabernat.github.io/research_computing/parallel-programming-with-mpi-for-python.html
if runMPI:
    subsetCM=comm.bcast(subsetCM,root=0) #this is a blocking call! explain!
    
#lets debug some...
#print('type  of subsetCM for rank',rank,'is',type(subsetCM),flush=True)
#print('shape of subsetCM for rank',rank,'is',subsetCM.shape,flush=True)

if rank==0:
    print('done subsetting CM in',time.time()-tic,'domain size',subsetCM.shape[0],flush=True)
    print('   the CM matrix has a sparsity',subsetCM.nnz/np.prod(subsetCM.shape),flush=True)
tic=time.time()

#=====================================================================
# The code has now completed the steps that all ranks do in the same way.
# The code below only creates the population matrix for a subset of the
# model. The limits of each subset goes from pmBounds[rank]:pmBounds[rank+1]
fullDomSize=subsetCM.shape[0]
pmBounds=np.linspace(0, fullDomSize, size + 1).round().astype(int)

#It is more convienient if the species length is not the same as the
#domain size, so that errors in how we address the matrices are
#caught.  So if true, change pmBounds so that the last and first
#species in domain do not have a species starting in them. Is this an
#issue? Note that this is for the entire domain, not a single rank...
if True:
    pmBounds[0]=pmBounds[0]+1
    pmBounds[-1]=pmBounds[-1]-1

print('   rank %0.0d runing species %0.0d to %0.0d'%(rank,pmBounds[rank],pmBounds[rank+1]),flush=True) 

# WARNING, THE FOLLOWING TEXT IS IMPORTANT, AND SHOWS HOW THE
# DIFFERENT RANKS OF THE MPI JOB FIT TOGETHER. Remember that the
# population matrix sampMat is defined so
# sampMat(whichSpecies,whereInSpace) and the connectivity matrix is
# define so that subsetCM(whereFrom,whereTo).
#
# Here we create the initial population matrix, sampMat. For the full
# matrix, it would be 1.0 on the diagonal. But we are breaking this
# problem up so different species run in different ranks. So for the
# chunk of the matrix we are doing when we break this problem up into
# chunks of species, it is a bit more complicated. The indices into
# the connectivity matric subsetCM are the same indices as they would
# be if we were to run as a single process. The columns of the species
# density data (in sampMat) share the same index to real world
# mapping. However, the rows into sampMat have changed. Row 0 no
# longer indicates the species that started at location 0 in
# subsetCM. It is starting at pmBounds[rank]. So, what would be row
# iFull in subsetCM is row iFull-pmBounds[rank] in sampMat.

#sampMat = np.zeros((pmBounds[rank+1]-pmBounds[rank]+1,fullDomSize),dtype=popMatType)
sampMat = np.zeros((pmBounds[rank+1]-pmBounds[rank],fullDomSize),dtype=popMatType)
for iWhere in np.arange(pmBounds[rank],pmBounds[rank+1]): #where does the species go
    sampMat[iWhere-pmBounds[rank],iWhere] = 1.0

for pt in exPoints:
    sampMat[:,pt] = np.zeros(len(sampMat[:,pt]))
    
if rank==0:
    print('made initial condition in',time.time()-tic,flush=True)
    print('done setting up model',flush=True)

#Run model forward in time.
if True:

    saveArr = [] #save data to plot below   
    for gen in range(nGenMax+1):
        t1 = time.time()

        #if condition is met, save data.  THIS IS DONE FIRST so that
        #gen=0 is the initial condition, gen=1 is after 1 time step,
        #etc...
        if gen in whenSave:
            #save data in outDir/genName/fileName
            #make sure fileName sorts from smallest to larges rank
            #this makes combining them easier
            genName='gen_%5.5d/'%(gen,)
            fileName='rank%5.5d_of%0.0d.nc'%(rank,size)

            #now, we only want to create the data directory in rank 0
            #and we don't want any other process to write to directory
            #before it exists. So block until rank 0 is done
            if rank==0:
                os.mkdir(outDir+genName)
            if runMPI:
                #wait till everyone reaches this point, and we know
                #data directory has been made
                comm.Barrier() 

            #now each process can write its data
            chunkBounds=np.array([pmBounds[rank],pmBounds[rank+1]])+0
            dims=['nSpecies','nLocation','gen']
            coords=dict(nSpecies=(['nSpecies'],np.arange(pmBounds[rank],pmBounds[rank+1])),
                        nLocation=(['nLocation'],np.arange(0,subsetCM.shape[0])),gen=('gen',[gen]),
                        latVec=(['nLocation'],latVec),
                        lonVec=(['nLocation'],lonVec)
            )
            dataVars={'popMatrix':(['gen','nSpecies','nLocation'],np.expand_dims(sampMat,0)),
           #           'lonVec':(['nLocation'],lonVec),
           #           'latVec':(['nLocation'],latVec)
            }
            xr.Dataset(data_vars=dataVars,#dims=dims,
                       coords=coords).to_netcdf(outDir+genName+fileName,
                                                     engine='netcdf4',
                                                     encoding={'popMatrix':{"zlib": True,"complevel": 1}})
            #breakpoint()

            if rank==0:
                print('   Done saving data',flush=True)

        
        #comment old code, replace with in place
        sampMat = sampMat@subsetCM

        for pt in exPoints:
            sampMat[:,pt] = np.zeros(len(sampMat[:,pt]))

        #now normalize; this code might be able to be optimized,
        #but don't due so till in realistic pop distribution,
        #for normalization will be dependent on number of locations
        #with no larvae reaching them. First calculate number of
        #larvae reaching a point
        numSettle=np.sum(sampMat, axis=0)

        #this is where we will sum all the populations on different
        #processes if running in MPI. At the end of this, numSettle
        #will have the number of settelers for all places in all ranks.
        if runMPI:
            #first, use Reduce to sum all the numSettle in different
            #ranks. The answer will given to rank 0, and the answer will be
            #put in numSettleAll on rank0
            numSettleAll=np.zeros(numSettle.shape,dtype=popMatType)
            comm.Reduce(numSettle,numSettleAll,op=MPI.SUM,root=0)

            #if rank 0, then put the total from numSettleAll in numSettle
            if (rank==0):
                #copy answer to numSettle, and then broadcast to other ranks
                numSettle=numSettleAll.copy()
                
            #now broadast numSettle to all of the other ranks. This takes the value
            #of numSettle in rank=0 and puts in the numSettle of the other ranks. 
            comm.Bcast(numSettle,root=0)
                
        #now this is tricky. if no larvae reach a point, numSettle at
        #that point will be 0. In the normalization below, this leads to
        #0/0 and a nan, which then breaks things. but if no points are
        #reaching a point, then we can normalize by anything, since 0/anything
        #is zero. So replace 0's with 1's in numSettle.
        numSettle[numSettle==0.0]=1.0 #deal with nan's when no larvae reach a point

        #now normalize
        sampMat = sampMat/numSettle #note: sum is vector, then broadcast
        #breakpoint()

        pointToPrint=18500
        if (pointToPrint>=pmBounds[rank]) & (pointToPrint<pmBounds[rank+1]):
            saveVec=(sampMat[pointToPrint-pmBounds[rank]]+0.0)
            print('   Run for rank %d of %d done in'%(rank,size),time.time()-t1,'s','pop sum is',
                  sum(saveVec),flush=True)
        #else:
        #    print('   Run for rank %d of %d done in'%(rank,size),time.time()-t1,'s',flush=True)
            

        #this blocks until all processes reach this point before
        #starting next generation.  this is not strictly necessary,
        #but it helps perserve my sanity when debugging.
        if runMPI:
            comm.Barrier()
        if rank==0:
            print('   done with gen',gen,flush=True)
            print(' ',flush=True)
