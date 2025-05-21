from pylab import *
from numpy import *
import xarray as xr
import glob
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import time
from os import path

#what directory to get data from
#dDir = '/data/break/pringle/willModelMPIdata/'
dDir = '/data/guppy/willlush/neutralModelMPI_output/'
#dataDir=dDir+'souPac_data_season_spr_PLD3_cPer1/'
dataDir=dDir+'norPac_data_season_spr_PLD30_cPer10/'
#dataDir=dDir+'souPac_data_season_spr_PLD30_cPer10/'
#dataDir=dDir+'indPac_data_season_spr_PLD30_cPer10/'
#dataDir=dDir+'fulInd_data_season_spr_PLD30_cPer10/'

#read in data, sort, and read
allFileNames=glob.glob(dataDir+'*[0123].nc')
allFileNames=glob.glob(dataDir+'*.nc')
allFileNames=sorted(allFileNames)
data=xr.open_mfdataset(allFileNames,combine='nested',concat_dim='gen',chunks={'nSpecies':100})
    
#by looking at the gen=0 time record, figure out which species start
#in an area selected on map. At the end of this, the vector of booleans inBounds
#will be true for all locations in lonVec and latVec that are in the selected polygon
assert data["gen"][0].values == 0,'need gen=0 a to find where species start!'
figure(1,figsize=(9.0,9.0))
style.use('ggplot')
clf()
axBig=gca() #save axis so we can use later 

lonVec=data["lonVec"].values
latVec=data["latVec"].values
plot(lonVec, latVec, "k,") #,alpha=0.7)

if path.exists('indoPacific_removePoints.npz'):
    getPoints = np.load('indoPacific_removePoints.npz')
    loadLat = getPoints['latVec']
    loadLon = getPoints['lonVec']
    plot(loadLon,loadLat,'g.')
else:
    loadLat = []
    loadLon = []

pause(0.1)

if True:
    #interactively select points to look at
    print('ZOOM TO DESIRED LEVEL, THEN HIT ENTER')
    selection_ready=False
    while selection_ready==False:
        selection_ready = waitforbuttonpress()
        print('PLEASE SELECT REGION AND HIT ENTER')

    bounds=ginput(n=-1,timeout=-1,show_clicks=True)

    polyBounds=Polygon(bounds)
    #print('finding points in bounds')
    points=[Point(x[0],x[1]) for x in list(zip(lonVec,latVec))]
    #print('  got points')
    inBounds=array([polyBounds.contains(point) for point in points])
    #print('  done')

#now plot origin of these points on initial map as a scatter plot of
#their final total population. Plot so biggest values are at top. 
lon2plot=np.append(lonVec[inBounds],loadLon)
lat2plot=np.append(latVec[inBounds],loadLat)
sca(axBig)
plot(lon2plot,lat2plot,'r.')

tight_layout()
show()
draw()
pause(0.1)

if False:
    np.savez('indoPacific_removePoints.npz',lonVec=lon2plot,latVec=lat2plot)
