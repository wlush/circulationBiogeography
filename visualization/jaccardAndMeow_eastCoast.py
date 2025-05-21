import pylab as p
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as ftr
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
from cartopy.geodesic import Geodesic
import shapely

#MEOW shapefile, with some hacks to prevent anitmeridian issues:
dnDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'

#subregion
figsize=(9,9)
minLon=-78.0; maxLon=-63.25
minLat=34.5; maxLat=47.0
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
#figsize=(12,10)

#plot jaccard vals...
fig = p.figure(figsize=figsize, constrained_layout=True)
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
    ax.add_geometries((geom,), crs=ccrs.PlateCarree(), facecolor='none', edgecolor='blue',lw=1.5,linestyle='dashed',zorder = 100,label='blue')

ecoRegionList = [er for er in reader.records()]#[0]
for ecoRegion in ecoRegionList:
    if int(ecoRegion.attributes['ECO_CODE_X'])!=62:
        shape_feature = ShapelyFeature([ecoRegion.geometry], ccrs.PlateCarree(), edgecolor='purple', facecolor='none',lw=1.5)
        ax.add_feature(shape_feature,zorder = 50)

#load model bounds:
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
import matplotlib.lines as mlines
mb = mlines.Line2D([], [], color='red', marker='*', linestyle='None',
                          markersize=10, label='model boundaries')
meb = mlines.Line2D([], [], color='purple', marker='None',label='MEOW ecoregion boundaries')
uc = mlines.Line2D([], [], color='blue', marker='None',linestyle='dashed',label='Uncertainty radius')
ax.legend(handles=[mb,meb,uc],loc='lower right')
sct = ax.scatter(jLon[jOrder],jLat[jOrder],c=jJac[jOrder],vmax = .5,zorder=100)
ax.plot(pickedLon,pickedLat,marker='*',markersize=20,color = 'red',linestyle='none',zorder=110)
p.colorbar(sct,fraction=0.04, pad=0.03,label='Jaccard difference \n(fractional change in model species assemblage)',orientation='horizontal')
#p.tight_layout()
p.show()

if True:
    p.savefig('eastCoast_jaccardMEOW.png',dpi = 500)
