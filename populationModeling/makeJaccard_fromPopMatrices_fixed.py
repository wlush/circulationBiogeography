import numpy as np
import pylab as p
import netCDF4 as nc
import pandas as pd
from os import path
import scipy.spatial.distance as ssd
from sklearn.neighbors import BallTree,DistanceMetric
#import shapefile as sf
import xarray as xr
import shapely
from shapely.geometry import Point
import glob

dDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'
import sys
sys.path.insert(0, dDir) #import modules from /Popmodel directory
import tagToLoc as ttl
import fixOffByOne as fob

# print('THIS LOOKS AT JACCARD LOCATION-BY-LOCATION; OTHER JACCARD LOOKS AT SIMILARITY OF DISTRIBUTIONS ALONGSHORE SPECIES-BY-SPECIES')

#load landmask
testname = '/data/guppy2/willlush/Mercator/cGrid/trmSymlinks/Mask.nc'
lm = nc.Dataset(testname,'r')
tM = lm['tmask'][0,0,:,:].data.astype(bool)
lm.close()

#caseList = ['Atlantic','norPac','souPac','indPac']#,'fulInd']
#caseList = ['norPac','souPac','fulInd']
#caseList = ['Atlantic',]
#caseList = ['fulInd',]
caseList = ['indPac',]
seasonList = ['win','sum','spr','fal']
#seasonList = ['win',] # 'sum']
pldDict = {3:1, 15:6, 30:10, 45:20}

# caseList = ['Atlantic',]
# seasonList = ['sum',]
# pldDict = {45:20}

# caseList = ['norPac',]
# seasonList = ['fal',]
# pldDict = {3:1}

def getJaccard(index,binaryMatrix):
    base = binaryMatrix[:,index]
    neighbors = nInd[index] #indices of neighbors
    neighDist = nDist[index] #distance of neighbors
    compareInd = neighbors[np.argmax(neighDist)]
    compare = binaryMatrix[:,compareInd]
    jacDiff = ssd.jaccard(base,compare)
    return(jacDiff)

for case in caseList:
    for season in seasonList:
        for pld in pldDict.keys():
            cPer = pldDict[pld]
            print(case,season,pld)  
            #location of population matrices
            pmLoc = '/data/guppy/willlush/neutralModelMPI_output/'
            #pmLoc = '/data/guppy/willlush/neutralModelMPI_output/indoPacific_toZip/'
            dataDir = pmLoc + '%s_data_season_%s_PLD%s_cPer%s/'%(case,season,pld,cPer)
            
            sName = pmLoc+'jaccard/%s_%s_pld%s_withIP_minus3.nc'%(case,season,pld)
            if path.exists(sName):
                print('already run, continuing')
                continue
            else:
                #read in data, sort, and read in
                allFileNames=glob.glob(dataDir+'*[0123].nc')
                allFileNames=glob.glob(dataDir+'*.nc')
                allFileNames=sorted(allFileNames)
                try:
                    data=xr.open_mfdataset(allFileNames,combine='nested',concat_dim='gen',chunks={'nSpecies':100})
                except OSError:
                    print('no file to input; continuing')
                    continue


                generations = data['gen'].values
                latVec = data['latVec'].values[1:-1]
                lonVec = data['lonVec'].values[1:-1]

                #build balltree and find neighbors
                latLonPairs=np.radians(list(zip(latVec,lonVec)))

                earthRad = 6371 #Earth's radius in km - for computing distances in radians
                neighborRadius = 25
                anRad = neighborRadius/earthRad
                neighborTree = BallTree(latLonPairs,metric='haversine')

                nInd, nDist = neighborTree.query_radius(latLonPairs,r=anRad,return_distance=True)

                binMatrix = data['popMatrix']>=(10.e-3) #-5) get data into binary for jaccard computation

                for genIndex in np.arange(len(generations)):
                    print(generations[genIndex])
                    whatGen = generations[genIndex]

                    jacVal = []

                    bMatrix = binMatrix[genIndex,:,:].values
                    ####FOR SANITY CHECK RUN ON GENERATION 0 - ALL SHOULD BE 1!###
                    ### bMatrix = binMatrix[0,:,:].values
                    for ix in np.arange(len(data['nSpecies'].values)): #Jaccard diff between focal point and furthest neighbor
                        jacVal.append(getJaccard(ix,bMatrix))

                    jacVal = np.array(jacVal)
                    #daJacVal = xr.DataArray(data=jacVal) #dataVar)
                    if genIndex==0:
                        dataVars = jacVal.copy()
                    else:
                        dataVars = np.vstack((dataVars,jacVal))

                # Define data with variable attributes
                ix = np.arange(len(jacVal))
                #data_vars = {'Jaccard':(['gen','ix'], [np.array(jacVal)]),'lon': (['ix'], lonVec),'lat':(['ix'],latVec)}
                dataV={'jacIndex':(['gen','nLocation'],dataVars),
                       'lonVec':(['nLocation'],lonVec),'latVec':(['nLocation'],latVec)}
                coords = {'loc_Index':(['ix'],ix),'gen':(['gen'],generations)}
                #testds = xr.Dataset(data_vars=data_vars,coords=coords,)
                jacds = xr.Dataset(data_vars=dataV,coords=coords,)
                assert True
                print('saving')
                if True:
                    jacds.to_netcdf(sName,engine='netcdf4',
                                    encoding={'jacIndex':{"zlib": True,"complevel": 1}})

if False:
    print('Jaccard testing')
    plOrder = np.argsort(jacVal)
    fig = px.scatter_geo(jacVal[plOrder],lat=latVec[plOrder],lon=lonVec[plOrder],color = jacVal[plOrder])
    fig.update_layout(title = 'World map', title_x=0.5)
    fig.show()
