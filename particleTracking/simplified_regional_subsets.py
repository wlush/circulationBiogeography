import pylab as p
import numpy as np
import xarray as xr
import netCDF4 as nc
import glob
import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import time

print('latest as of December 19th 2022 - just for regions in paper')

analysis_regions = ['global',]

caseList = ['Atlantic','norPac','souPac','fulInd','indPac']
genList = [0, 1, 2, 3, 4, 5, 10, 25, 50, 75, 100, 250, 500, 750, 999, 1000]

gC = np.load('fixed_regional_meow_subsets.npz',allow_pickle=True)
extantRegions = list(gC['meCount'].item().keys())

pCount = {}
pick_subsets = {}
for gen in np.arange(len(genList)):
    generation = genList[gen]
    for season in ['win','spr','sum','fal']:
        for PLD in [3,15,30,45]:
            for whatRegion in analysis_regions:
                # bLon = []
                # bLat = []
                # for case in caseList:
                #     dDir = '/data/guppy/willlush/neutralModelMPI_output/jaccard/'
                #     dataName=dDir+'%s_%s_pld%s_withIP_minus3.nc'%(case,season,PLD)

                #     data = xr.load_dataset(dataName)

                #     lonVec=bLon.extend(data["lonVec"].values)
                #     latVec=bLat.extend(data["latVec"].values)

                # bLon = np.array(bLon)
                # bLat = np.array(bLat)

                pickName ='automated_boundaries/autoBounds_clusterMax_%s_PLD%s_gen%s.npz'%(season,PLD,generation)
                pickedLoad = np.load(pickName)
                pLat = pickedLoad['pickedLat']
                pLon = pickedLoad['pickedLon']

                irLat = pLat
                irLon = pLon
                irLat = np.array(irLat)
                irLon = np.array(irLon)

                #low latitudes
                lnMask = (irLat<30)&(irLat>=0)
                lsMask = (irLat>-30)&(irLat<=0)
                lbMask = lnMask | lsMask

                #mid latitudes
                mnMask = (irLat<60)&(irLat>=30)
                msMask = (irLat>-60)&(irLat<=-30)
                mbMask = mnMask | msMask

                #high latitudes - only NH
                hnMask = irLat>=60

                #northern hemisphere
                nHemiMask = irLat>=0

                #southern hemisphere
                sHemiMask = irLat<=0

                #all
                allPicked = np.ones(len(irLat)).astype(bool)

                masks = [lnMask,lsMask,lbMask,mnMask,msMask,mbMask,hnMask,nHemiMask,
                         sHemiMask,allPicked]
                mName = ['nh low','sh low','both low','nh mid','sh mid','both mid','nh high',
                         'nh full','sh full','full']

                for ix in np.arange(len(masks)):
                    saveTuple = (season, PLD, whatRegion,mName[ix],generation)
                    print(saveTuple,generation)
                    print(len(irLon[masks[ix]]))
                    if len(irLon[masks[ix]])!=0:
                        latSub_latLon = list(zip(irLat[masks[ix]],irLon[masks[ix]]))
                        pick_subsets[saveTuple]=latSub_latLon
                        pCount[saveTuple] = len(irLon[masks[ix]])

if True:
    np.savez('automated_bounds_regionalSubset_max_allGen.npz',pCount = pCount, pick_subsets = pick_subsets)               
                
