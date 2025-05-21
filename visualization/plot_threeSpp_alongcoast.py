import pylab as p
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as ftr
import glob
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import time

#What directory to get data from
dDir = '/data/guppy/willlush/neutralModelMPI_output/'
dataDir=dDir+'Atlantic_data_season_spr_PLD30_cPer10/'

#read in data, sort, and read in
allFileNames=glob.glob(dataDir+'*[0123].nc')
allFileNames=glob.glob(dataDir+'*.nc')
allFileNames=sorted(allFileNames)
data=xr.open_mfdataset(allFileNames,combine='nested',concat_dim='gen',chunks={'nSpecies':100})

#subregion
figsize=(9,10)
minLon=-78.0; maxLon=-60.0
minLat=35.0; maxLat=47.0

axisVec=(minLon,maxLon,minLat,maxLat)

genList = data['gen'].values
newGenList = [0,10,100,1000]

threshold = .001

lonVec=data["lonVec"].values
latVec=data["latVec"].values
lonLat = list(zip(lonVec,latVec))
coastPoints = [Point(x) for x in lonLat]

fig = p.figure(1,figsize=figsize)
p.clf()

ax1 = fig.add_subplot(2,2,1,projection=ccrs.PlateCarree())
ax2 = fig.add_subplot(2,2,2,projection=ccrs.PlateCarree())
ax3 = fig.add_subplot(2,2,3,projection=ccrs.PlateCarree())
ax4 = fig.add_subplot(2,2,4,projection=ccrs.PlateCarree())

for i in np.arange(len(newGenList)):
    cAx = fig.axes[i]
    cAx.set_title('%s gens'%(newGenList[i]))
    #ax1.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    #gl.top_labels = False
    #gl.right_labels = False
    cAx.add_feature(ftr.LAND,facecolor='tab:grey')
    cAx.add_feature(ftr.OCEAN,facecolor='tab:grey',alpha=.05)
    # cAx.add_feature(ftr.COASTLINE,linewidth=0.3)
    cAx.set_extent(axisVec,crs=ccrs.PlateCarree())

    
    gIx = np.nonzero(genList==newGenList[i])[0]
    sPt1 = Point(-68.91,44.314)
    near1 = np.argmin([sPt1.distance(x) for x in coastPoints])
    pm1 = data['popMatrix'][gIx,near1,:].values
    pm1[pm1<threshold] = 0
    cAx.scatter(lonVec,latVec,s=100*pm1,zorder=100)

    sPt2 = Point(-64.6797,45.6805)
    near2 = np.argmin([sPt2.distance(x) for x in coastPoints])
    pm2 = data['popMatrix'][gIx,near2,:].values
    pm2[pm2<threshold] = 0
    
    if i!=0:
        cAx.scatter(lonVec,latVec,s=1000*pm2,zorder = 50)
    else:
        cAx.scatter(lonVec,latVec,s=100*pm2,zorder = 50)

    sPt3 = Point(-71.07,41.43)
    near3 = np.argmin([sPt3.distance(x) for x in coastPoints])
    pm3 = data['popMatrix'][gIx,near3,:].values
    pm3[pm3<threshold] = 0
    cAx.scatter(lonVec,latVec,s=100*pm3,zorder=100)

p.tight_layout()
#p.savefig('four_gens_eastCoast.png')
p.show()
