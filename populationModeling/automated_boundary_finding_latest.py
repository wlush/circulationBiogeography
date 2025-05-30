import numpy as np
import pylab as p
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import pyproj
import sys

from sklearn.neighbors import BallTree,DistanceMetric
from sklearn.metrics.pairwise import haversine_distances
from sklearn.cluster import DBSCAN
from shapely.geometry import LineString, Point
import shapely.geometry
from shapely.ops import transform
import geopandas as gpd
import glob
from functools import partial
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import cartopy.feature as ftr

print('automated code for finding model boundaries\n')

#parameters to pick points
earthRad = 6371 #Earth's radius in km - for computing distances in radians

caseList = ['Atlantic','norPac','souPac','fulInd','indPac']
pldList = [3,15,30,45]
seaList = ['win','spr','sum','fal']

pldList = [30]
seaList = ['spr']

meowLoad = np.load('cleaned_meow_intersections.npz')
meowLat = meowLoad['mLat']
meowLon = meowLoad['mLon']

saveDir = '/data/guppyhome/willlush/workfiles/trm_big_runs/analysisCode/analysisFromJamie/automated_boundaries/'

#seaList = ['win']
#pldList = [30]

for season in seaList:
    for pld in pldList:
        for gen in np.arange(16): #hardcoded, dumb, fix later...
        #create global map of jaccard indices
            cLon = []
            cLat = []
            cJac = []
            combDict = {}
            for case in caseList:
                dDir = '/data/guppy/willlush/neutralModelMPI_output/jaccard/'
                dataName=dDir+'%s_%s_pld%s_withIP_minus3.nc'%(case,season,pld)
                dataName=dDir+'%s_%s_pld%s_withIP_test_minus2.nc'%(case,season,pld)
                dataName = dDir+'%s_%s_pld%s_withIP_test_minus5.nc'%(case,season,pld)

                data = xr.load_dataset(dataName)
                generation = data.gen.values[gen]

                lonVec = data["lonVec"].values
                lon1 = ~np.isin(lonVec,[-58.916668,-59.,-77.5,-77.416664]) #overlap points
                latVec = data["latVec"].values
                lat1 = ~np.isin(latVec,[7.891596,7.891596,6.154795,5.9890637]) #overlap points
                ll = lat1|lon1
                lonLat = list(zip(lonVec[ll],latVec[ll]))

                jacVec = data["jacIndex"][-1,:].values
                jacVec = data['jacIndex'][gen,:].values
                jacVec = jacVec[ll]
                #cJac.extend(jacVec)
                cD = dict(zip(lonLat,jacVec))

                for key in cD.keys():
                    if key in combDict.keys():
                        combDict[key] = (combDict[key]+cD[key])/2
                    else:
                        combDict[key] = cD[key]

            cLon = [x[0] for x in combDict.keys()]
            cLat = [x[1] for x in combDict.keys()]
            cJac = list(combDict.values())

            tLon = np.array(cLon)
            tLat = np.array(cLat)
            tJac = np.array(cJac)

            cjMask = ~np.isinf(np.log10(tJac))
            cLon = tLon[cjMask]
            cLat = tLat[cjMask]
            cJac = tJac[cjMask]

            #load some points to remove
            #indo-pacific
            getPoints = np.load('indoPacific_removePoints.npz')
            loadLat = getPoints['latVec']
            loadLon = getPoints['lonVec']

            getRegions = np.load('analysis_regions.npz',allow_pickle=True)
            regions = getRegions['regions'].item()
            #arctic archipelago, svalbard, novaya zemlya
            toRm = []
            for reg in ['arctic_archipelago','svalbard','novaya_zemlya']:
                toRm.extend(regions[reg])
            toRm = list(dict.fromkeys(toRm)) #unique tuples
            trLon,trLat = list(zip(*toRm))

            loadLat = np.append(loadLat,trLat)
            loadLon = np.append(loadLon,trLon)

            mskA = np.isin(cLat,loadLat)
            mskB = np.isin(cLon,loadLon)
            mskC = (mskA & mskB)

            indices = np.arange(len(cLon))[mskC]
            cLon = np.delete(cLon,indices)
            cLat = np.delete(cLat,indices)
            cJac = np.delete(cJac,indices)

            #threshold for jaccard difference
            cjMask = cJac>.25 
            cLon = cLon[cjMask]
            cLat = cLat[cjMask]
            cJac = cJac[cjMask]
            plotOrder = np.argsort(cJac)
            #try lat, lon instead of lon, lat:
            radLatLon = np.radians(list(zip(cLat,cLon)))
            cTree = BallTree(radLatLon,metric='haversine')

            X = np.radians(list(zip(cLat,cLon)))
            #try finding clusters using DBSCAN
            #clustering = DBSCAN(eps=50/earthRad,min_samples=3,metric='haversine').fit(X) #MIN SAMPLES IS TOTAL WEIGHT...
            clustering = DBSCAN(eps=50/earthRad,min_samples=3,metric='haversine').fit(X)

            #1. start by finding neighbors only for points with a Jaccard diff over .25
            nInd = cTree.query_radius(radLatLon,r=50/earthRad)

            bigArr = []
            sInd = [set(x) for x in nInd]
            if False:
                for ix in np.arange(len(sInd)):
                    ngh = sInd[ix]
                    end=False
                    while end==False:
                        test1 = len(ngh)
                        addTo = set().union(*[sInd[x] for x in ngh])
                        ngh = ngh.union(addTo)
                        test2 = len(ngh)
                        if test1==test2:
                            if np.all([len(ngh.intersection(bigArr[x]))==0 for x in np.arange(len(bigArr))]):
                                if len(ngh)>3: #threshold for boundaries 
                                    bigArr.append(ngh)
                                    end=True
                            else:
                                [bigArr[x].union(ngh) for x in np.arange(len(bigArr)) if len(ngh.intersection(bigArr[x]))>0 ]
                                end=True


                    assert len(bigArr)==len(np.unique(clustering.labels_)),'DBSCAN and hard-coded not the same...'
            if False:
                #visualize clusters
                p.figure(figsize=(12.,10.))
                p.clf()
                cMap = p.axes(projection=ccrs.PlateCarree())
                cMap.add_feature(ftr.COASTLINE,linewidth=0.3)
                p.rcParams['axes.facecolor'] ='white'

                # Read shape file
                dnDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'
                reader = shpreader.Reader(dnDir+'MEOW/meow_ecos.shp')

                ecoRegionList = [er for er in reader.records()]#[0]
                for ecoRegion in ecoRegionList:
                    shape_feature = ShapelyFeature([ecoRegion.geometry], ccrs.PlateCarree(), edgecolor='purple', facecolor='none',lw=1)
                    cMap.add_feature(shape_feature,zorder = 50,linewidth=.5)

                for label in np.unique(clustering.labels_):
                    labMask = np.nonzero(clustering.labels_==label)
                    if label==-1:
                        p.plot(cLon[labMask],cLat[labMask],'.',c='lightgrey',alpha=.25)
                    else:
                        p.plot(cLon[labMask],cLat[labMask],'.')

                p.plot(boundLon,boundLat,'r*',markeredgecolor='k',zorder=150)    
                p.tight_layout()
                p.show()
                p.draw()
                p.pause(0.1)
                assert False

            boundLon = []
            boundLat = []    
            if True: #FIND MAXIMUM VALUE IN CLUSTER   
                for label in np.unique(clustering.labels_):
                    if label >= 0: #for labels included in clustering
                        labMask = np.nonzero(clustering.labels_==label)

                        #find location of maximum jaccard within cluster
                        locLon = cLon[labMask]
                        locLat = cLat[labMask]
                        locMax = np.argmax(cJac[labMask])

                        boundLon.append(locLon[locMax])
                        boundLat.append(locLat[locMax])
            if False: #FIND CENTROID OF CLUSTER
                for label in np.unique(clustering.labels_):
                    if label >= 0: #for labels included in clustering
                        labMask = np.nonzero(clustering.labels_==label)

                        #find location of centroid of cluster:
                        centLon = np.mean(cLon[labMask])
                        centLat = np.mean(cLat[labMask])

                        centLoc = np.radians([centLat,centLon])
                        compLocs = np.radians(list(zip(cLat[labMask],cLon[labMask])))
                        getDist = haversine_distances([centLoc],Y=compLocs) 
                        argNear = np.argmin(getDist) #find nearest point in cluster

                        ncLon = cLon[labMask][argNear]
                        ncLat = cLat[labMask][argNear]

                        # boundLon.append(centLon)
                        # boundLat.append(centLat)

                        boundLon.append(ncLon)
                        boundLat.append(ncLat)

            if False:
                #visualize clusters
                p.figure(figsize=(12.,10.))
                p.clf()
                cMap = p.axes(projection=ccrs.PlateCarree())
                cMap.add_feature(ftr.COASTLINE,linewidth=0.3)
                p.rcParams['axes.facecolor'] ='white'

                # Read shape file
                dnDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'
                reader = shpreader.Reader(dnDir+'MEOW/meow_ecos.shp')

                ecoRegionList = [er for er in reader.records()]#[0]
                for ecoRegion in ecoRegionList:
                    shape_feature = ShapelyFeature([ecoRegion.geometry], ccrs.PlateCarree(), edgecolor='purple', facecolor='none',lw=1)
                    cMap.add_feature(shape_feature,zorder = 50,linewidth=.5)

                #create circles...
                #draw circles
                stdDist = 326.82947 #std dist btw MEOW points in km
                from shapely.ops import transform
                
                mR2 = []
                for i in np.arange(len(meowLat)):
                    radius = (stdDist/2)*1000  # in m
                    
                    local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(
                        meowLat[i], meowLon[i]
                    )
                    wgs84_to_aeqd = partial(
                        pyproj.transform,
                        pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
                        pyproj.Proj(local_azimuthal_projection),
                    )
                    aeqd_to_wgs84 = partial(
                        pyproj.transform,
                        pyproj.Proj(local_azimuthal_projection),
                        pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
                    )

                center = Point(float(meowLon[i]), float(meowLat[i]))
                point_transformed = transform(wgs84_to_aeqd, center)
                buffer = point_transformed.buffer(radius)
                # Get the polygon with lat lon coordinates
                circle_poly = transform(aeqd_to_wgs84, buffer)
                mR2.append(circle_poly)

                for label in np.unique(clustering.labels_):
                    labMask = np.nonzero(clustering.labels_==label)
                    if label==-1:
                        p.plot(cLon[labMask],cLat[labMask],'.',c='lightgrey',alpha=.25)
                    else:
                        p.plot(cLon[labMask],cLat[labMask],'o',c='y')

                p.plot(boundLon,boundLat,'r*',markeredgecolor='k',zorder=150)    
                p.tight_layout()
                p.show()
                p.draw()
                p.pause(0.1)
                assert False


            print('saving %s PLD%s %s'%(season,pld,generation))
            if True:
                # np.savez(saveDir+'autoBounds_min3forCluster_%s_PLD%s.npz'%(season,pld),pickedLon=boundLon,pickedLat=boundLat)
                np.savez(saveDir+'autoBounds_clusterMax_%s_PLD%s_gen%s_smallThresh.npz'%(season,pld,generation),pickedLon=boundLon,pickedLat=boundLat)
            else:
                print('not saved!!!')
