import numpy as np
import pylab as p
import netCDF4 as nc
import xarray as xr
import pandas as pd
import plotly
import json
import pyproj

from sklearn.neighbors import BallTree,DistanceMetric
import plotly.express as px
from shapely.geometry import LineString, Point
import shapely.geometry
from shapely.ops import transform
import plotly.graph_objects as go
import geopandas as gpd
import glob
from functools import partial
import cartopy.crs as ccrs
import cartopy.feature as ftr
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature

earthRad = 6371 #Earth's radius in km - for computing distances in radians

#load meow intersections:
intDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/newModel_allSpecies/stats/'
intName = intDir+'intersectionPoints.shp'
intPts = gpd.read_file(intName)

rmList =[(-79.64390808,9.04155998),(179.9999999,68.992771),(179.9999999,65.03296966),
         (32.3458441,30.70702738),(-68.63336222182889,-52.64078610031331),
         (-77.19457763341951,34.63809846898976),
         (141.6457153938365,76.01808310454872),
         (141.54536543209773,74.92889974454769),
         (239.75057031895017-360.,75.82261760372639),
         (254.00362392053674-360.,75.05987697837885),
         (260.1493905810646-360.,73.94701596418294),
         (258.16735896335194-360.,72.33923595564401),
         (279.6881318276463-360.,74.9071584341431),
         (55.3894285576883,73.32588442881631),
         (120.30459118627833,22.576808331732657),
         (120.61228883188265,24.43535705036384),
         (281.7808230302768, 76.5172623130089),
         (257.4211366618612, 75.50533931540333),
         (270.6879244727426, 76.47735907124995),
         (263.05059077963926, 76.72568605751283),
         (279.8639541165554, 73.21575001602359),
         (293.97213097589747, 61.87983495431842),
         (298.7028685894537, 66.64646918632829),
         (284.26821323320456, 78.00419639395619),
         (102.06838511373932, 6.250794489544883),
         (144.70103073250357, -40.751287037681074)]

#load some more points to remove
getPoints = np.load('indoPacific_removePoints.npz')
loadLat = getPoints['latVec']
loadLon = getPoints['lonVec']
rmIp = list(zip(loadLon,loadLat))
rmList.extend(rmIp)

#rm arctic archipelago
getPoints = np.load('analysis_regions.npz',allow_pickle=True)
rmIp = getPoints['regions'].item()
# rmRg = rmIp['arctic_archipelago']
# rmList.extend(rmRg)
rmRg = []

rmRg.extend(rmIp['svalbard'])
rmList.extend(rmRg)

rmRg.extend(rmIp['novaya_zemlya'])
rmList.extend(rmRg)

rmLon,rmLat = list(zip(*rmList))
rmLatLon = list(zip(rmLat,rmLon))

intLat = []
intLon = []
for mltPt in intPts.geometry:
    for pt in mltPt:
        intLat.append(pt.y)
        intLon.append(pt.x)
        
# addPoints = [(35.8696430421296,.02268864216572875),(49.51874144072256,-1.8758279950082102),
#              (35.212306,-75.52645556),(69.65743822644838,176.85333825336818)]
addLat = np.array([35.8696430421296,49.51874144072256,35.212306,69.65743822644838,
                   62.728668524843975])
addLon = np.array([.02268864216572875,-1.8758279950082102,-75.52645556,176.85333825336818,
                   179.62128775992068])
addLon[addLon<0.0]+=360
        
intLatLon = list(zip(intLat,intLon))
illRad = np.radians(intLatLon)

#remove duplicate MEOW points...
closeTree = BallTree(illRad,metric='haversine')
ind, dis = closeTree.query_radius(illRad,r=100/earthRad, return_distance=True)

rmInd = []
for ix in np.arange(len(ind)):
    distArr = dis[ix]
    indArr = ind[ix]

    if indArr[0] not in rmInd:
        rmInd.extend(indArr[1:])

#remove unwanted points:
rmTree = BallTree(np.radians(rmLatLon),metric='haversine')
ind = rmTree.query_radius(illRad,r=10/earthRad)

for ix in np.arange(len(ind)):
    if len(ind[ix])!=0:
        rmInd.append(ix)

keepMask = np.ones(len(intLatLon))
for ix in np.unique(rmInd):
    keepMask[ix]=0
    
meowLatLon = np.array(list(zip(illRad[:,0][keepMask.astype(bool)],
                               illRad[:,1][keepMask.astype(bool)])))

mLat = np.array(intLat)[keepMask.astype(bool)]
mLon = np.array(intLon)[keepMask.astype(bool)]

#np.savez('cleaned_meow_intersections.npz',mLat=mLat,mLon=mLon)

if True:
    p.figure(1,figsize=(12.0,10.0))
    p.clf()
    cMap = p.axes(projection=ccrs.PlateCarree())
    cMap.add_feature(ftr.LAND, zorder = 100)
    cMap.add_feature(ftr.OCEAN, zorder = 25)
    cMap.add_feature(ftr.COASTLINE,linewidth=0.3)
    p.plot(mLon,mLat,'r.',zorder=100)
    p.tight_layout()
    p.show()
