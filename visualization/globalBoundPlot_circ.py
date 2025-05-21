import pylab as p
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as ftr
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
from cartopy.geodesic import Geodesic
import glob
import shapely # from shapely.geometry import Point
#from shapely.geometry.polygon import Polygon
from sklearn.neighbors import NearestNeighbors
import time

dnDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'

#subregion
figsize=(12,10)
minLon=-180.0; maxLon=180.0
minLat=-61.5; maxLat=90.0
axisVec=(minLon,maxLon,minLat,maxLat)

#plot jaccard vals...
fig = p.figure(figsize=figsize)
p.clf()
ax = p.axes(projection=ccrs.PlateCarree())
# Read shape file
reader = shpreader.Reader(dnDir+'MEOW/meow_ecos.shp')
if True:
    fCounter = 0
    counter = 0
    ecoRegionList = [er for er in reader.records()]#[0]
    exList = [29,38,62,63,64,65,73,74,77,78,79,96,97,98,105,106,114,120,121,122,
              123,124,125,135,147,148,149,151,152,153,154,155,156,158,159,160,161,
              162,163,164,165,172,173,174,179,186,189,194,195,197,198,212,213,214,
              215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,
              232,157,146,131,139,138,137,150,133,126,127,128,129,130,134,136,
              132,21]#117
    for ecoRegion in ecoRegionList:
        #assert False
        fCounter+=1
        if int(ecoRegion.attributes['ECO_CODE_X']) not in exList:
            shape_feature = ShapelyFeature([ecoRegion.geometry], ccrs.PlateCarree(), edgecolor='purple', facecolor='none',lw=1)
            ax.add_feature(shape_feature,zorder = 50)
            counter+=1
print(fCounter)
print(counter)
# #load meow points
intDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/'
intName = intDir+'cleaned_meow_intersections.npz'
intPts = np.load(intName)
mLat = intPts['mLat']
mLon = intPts['mLon']

plotRadius = 153.57 #in km
for ix in np.arange(len(mLat)):
    circ = np.asarray(Geodesic().circle(lon=mLon[ix], lat=mLat[ix],radius=plotRadius*1000., n_samples=100,endpoint=False))

    #fix long striping...
    cd = np.abs(circ[:,0]-np.roll(circ[:,0],1))
    if np.amax(cd)>180.:
        cMsk = circ[:,0]>0
        c1 = circ[cMsk]
        c2 = circ[~cMsk]
        for ci in [c1,c2]:
            geom = shapely.geometry.Polygon(ci)
            #ax.add_geometries((geom,), crs=ccrs.PlateCarree(), facecolor='none',edgecolor='k',zorder = 100,linewidth=.75)
            ax.add_geometries((geom,), crs=ccrs.PlateCarree(), facecolor='none',edgecolor='blue',zorder = 100,linewidth=.75)
    else:
        geom = shapely.geometry.Polygon(circ)
        #ax.add_geometries((geom,), crs=ccrs.PlateCarree(), facecolor='none',edgecolor='k', zorder = 100,linewidth=.75)
        ax.add_geometries((geom,), crs=ccrs.PlateCarree(), facecolor='none',edgecolor='blue',zorder = 100,linewidth=.75)


#load picked bounds:
loadDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/automated_boundaries/'
season = 'spr'
PLD = 30
numGen = 1000
loadPicked = np.load(loadDir+'autoBounds_clusterMax_%s_PLD%s_gen%s.npz'%(season,PLD,numGen),allow_pickle=True)
pickedLat = loadPicked['pickedLat']
pickedLon = loadPicked['pickedLon']

ax.add_feature(ftr.LAND,facecolor='tab:grey',zorder=75)
ax.add_feature(ftr.COASTLINE,linewidth=0.3)
ax.set_extent(axisVec,crs=ccrs.PlateCarree())
ax.plot(pickedLon,pickedLat,marker='*',color = 'red',linestyle='none',zorder=110)

p.tight_layout()
p.show()

if False:
    p.savefig('globalBounds_circles.png',dpi = 500)
