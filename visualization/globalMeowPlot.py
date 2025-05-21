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

#MEOW shapefile, with some hacks to prevent anitmeridian issues:
dnDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'

#subregion
figsize=(9,10)
minLon=-78.0; maxLon=-60.0
minLat=35.0; maxLat=47.0
axisVec=(minLon,maxLon,minLat,maxLat)

#load jaccard values...
intDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/draft9_figures/bokeh_interactive_plots/'
jacLoad = np.load(intDir+'jaccard_vals_1000gen.npz',allow_pickle=True)
jDict = jacLoad['jac'].item()
jLat = jDict[(30, 'spr', 'latitude')]
jLon = jDict[(30, 'spr', 'longitude')]
jJac = jDict[(30, 'spr', 'jaccard')]
jMask = jJac<.75
jLat = jLat[jMask]
jLon = jLon[jMask]
jJac = jJac[jMask]
jOrder = np.argsort(jJac)

threshold = .001
figsize=(12,10)

#plot jaccard vals...
fig = p.figure(figsize=figsize)
p.clf()
ax = p.axes(projection=ccrs.PlateCarree())
# Read shape file
reader = shpreader.Reader(dnDir+'MEOW/meow_ecos.shp')

# #load meow points
intDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/'
intName = intDir+'cleaned_meow_intersections.npz'
intPts = np.load(intName)
mLat = intPts['mLat']
mLon = intPts['mLon']

plotRadius = 153.57 #in km
for ix in np.arange(len(mLat)):
    circ = np.asarray(Geodesic().circle(lon=mLon[ix], lat=mLat[ix],radius=plotRadius*1000., n_samples=100,endpoint=False))
    geom = shapely.geometry.Polygon(circ)
    ax.add_geometries((geom,), crs=ccrs.PlateCarree(), facecolor='none', edgecolor='purple',zorder = 100)

ecoRegionList = [er for er in reader.records()]#[0]
for ecoRegion in ecoRegionList:
    shape_feature = ShapelyFeature([ecoRegion.geometry], ccrs.PlateCarree(), edgecolor='red', facecolor='none',lw=1)
    ax.add_feature(shape_feature,zorder = 50)

# #load picked bounds:
# loadDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/automated_boundaries/'
# season = 'spr'
# PLD = 30
# numGen = 1000
# loadPicked = np.load(loadDir+'autoBounds_clusterMax_%s_PLD%s_gen%s.npz'%(season,PLD,numGen),allow_pickle=True)
# pickedLat = loadPicked['pickedLat']
# pickedLon = loadPicked['pickedLon']

ax.add_feature(ftr.LAND,facecolor='tab:grey',zorder=75)
ax.add_feature(ftr.COASTLINE,linewidth=0.3)
#ax.set_extent(axisVec,crs=ccrs.PlateCarree())
ax.set_global()
#ax.scatter(jLon[jOrder],jLat[jOrder],c=jJac[jOrder],vmax = .5,zorder=100)
#ax.plot(pickedLon,pickedLat,marker='*',markersize=25,color = 'orange',linestyle='none',markeredgecolor='k',zorder=110)

p.tight_layout()
p.show()

if True:
    p.savefig('globalMEOW_circles.png',dpi = 500)
