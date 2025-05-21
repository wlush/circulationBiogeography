import pylab as p
import numpy as np
import xarray as xr
import netCDF4 as nc
import glob
import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import time

print('find MEOW boundaries within analysis regions and latitude subsets')
assert True, 'do not alter!!! -wgl 9/13/22 - altered by wgl 10/11/22 due to missing hatteras'

analysis_regions = ['australia','south_america','north_america','africa','asia','atlantic_basin','pacific_basin','indian_basin','mediterranean_sea','gulf_of_mexico_caribbean_sea','europe','global']
to_subset = ['south_america','north_america','africa','asia','atlantic_basin','pacific_basin','europe','global']

whatRegion = 'global'

season = 'spr'
PLD = 45
numGen = 1000
caseList = ['Atlantic','norPac','souPac','fulInd']

getCounts = np.load('fixed_regional_meow_subsets.npz',allow_pickle=True)
meCount = getCounts['meCount'].item()
meow_subsets = getCounts['meow_subsets'].item()

bLon = []
bLat = []
for case in caseList:
    dDir = '/data/guppy/willlush/neutralModelMPI_output/jaccard/'
    dataName=dDir+'%s_%s_pld%s_withIP_minus3.nc'%(case,season,PLD)
    #dataName=dDir+'none_none_pld30.nc'

    data = xr.load_dataset(dataName)
    
    lonVec=bLon.extend(data["lonVec"].values)
    latVec=bLat.extend(data["latVec"].values)

bLon = np.array(bLon)
bLat = np.array(bLat)

fName = 'analysis_regions.npz'
loadJnk = np.load(fName,allow_pickle=True)
regions = loadJnk['regions'].item()

regions.update({'global':list(zip(bLon,bLat))})

atlantic_basin = ['atlantic_northeast','iceland', 'uk_ireland',
                  'south_america_ec','north_america_ec',
                  'africa_wc', 'atlantic_northwest']
pacific_basin =  [ 'new_zealand', 'japanese_archipelago',
                   'east_asia','south_america_wc','north_america_wc',
                   'south_pacific_west_boundary']
indian_basin = ['arabian_red_seas', 'bay_of_bengal_indonesia',
                'africa_ec','australia_indian_ocean']
europe = ['baltic_sea', 'iceland', 'uk_ireland','europe_wc','europe_southern_coast']
asia = ['east_asia', 'russian_arctic']
combined_regions = ['atlantic_basin','pacific_basin','indian_basin','europe','asia']

for reg in combined_regions:
    if reg == 'atlantic_basin':
        regList = atlantic_basin
    elif reg == 'pacific_basin':
        regList = pacific_basin
    elif reg == 'indian_basin':
        regList = indian_basin
    elif reg == 'europe':
        regList = europe
    elif reg == 'asia':
        regList = asia
    else:
        assert False, 'Something has gone quite wrong'

    combList = []
    for region in regList: #atlantic_basin:
        combList.extend(regions[region])
    combList = list(dict.fromkeys(combList)) #unique tuples
    regions.update({reg:combList})

#load meow points
intDir = '/data/guppyhome/willlush/workfiles/trm_big_runs/analysisCode/analysisFromJamie/'
intName = intDir+'cleaned_meow_intersections.npz'
intPts = np.load(intName)
mLat = intPts['mLat']
mLon = intPts['mLon']
meowLatLon = list(zip(mLat,mLon))

#remove regions
toRm = []
for reg in ['arctic_archipelago','svalbard','novaya_zemlya']:
    toRm.extend(regions[reg])
toRm = list(dict.fromkeys(toRm)) #unique tuples

getPoints = np.load('indoPacific_removePoints.npz')
loadLat = getPoints['latVec']
loadLon = getPoints['lonVec']
rmIp = list(zip(loadLon,loadLat))
toRm.extend(rmIp)

toPlot = []
for reg in regions.keys():
    toPlot.extend(regions[reg])

toPlot = list(dict.fromkeys(toPlot)) #unique tuples

#fast removal of points
toRm = set(toRm)
toPlot = set(toPlot)
toPlot = toPlot.difference(toRm)
toPlot = list(toPlot)

regions['global']=toPlot

#plot latitudes...
plot_lons = np.linspace(-180.,180,5000)
eqLat = np.zeros(len(plot_lons))
latLow = np.full(len(plot_lons),30)
latHigh = np.full(len(plot_lons),60)
lineList = [0.0,30.0,-30.0,60.0,-60.0]

p.figure(figsize=(12,10))
p.clf()
p.rcParams['axes.facecolor'] = 'tab:grey'
rLon,rLat = list(zip(*regions[whatRegion]))
p.plot(rLon,rLat,'.')
p.plot(bLon, bLat, "k,",alpha=0.5)
[p.axhline(y=i,color='blue',linestyle='--') for i in lineList]
p.plot(mLon,mLat,'r*')
p.tight_layout()
p.show()
p.pause(0.1)
#interactively select points to look at
print('ZOOM TO DESIRED LEVEL, THEN HIT ENTER')
selection_ready=False
while selection_ready==False:
    selection_ready = p.waitforbuttonpress()
    print('PLEASE SELECT REGION AND HIT ENTER')

bounds=p.ginput(n=-1,timeout=-1,show_clicks=True)

polyBounds=Polygon(bounds)
points=[Point(x[0],x[1]) for x in list(zip(mLon,mLat))]
inBounds=np.array([polyBounds.contains(point) for point in points])


p.plot(mLon[inBounds],mLat[inBounds],'g*')
p.tight_layout()
p.pause(0.1)
p.draw()
p.show()

ir = np.array(meowLatLon)[inBounds]
irLat,irLon = list(zip(*ir))
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

#high latitudes
hnMask = irLat>=60
hsMask = irLat<=-60
hbMask = hnMask | hsMask

#northern hemisphere
nHemiMask = irLat>=0

#southern hemisphere
sHemiMask = irLat<=0

#all
allMeow = np.ones(len(irLat)).astype(bool)

masks = [lnMask,
         lsMask,
         lbMask,
         mnMask,
         msMask,
         mbMask,
         hnMask,
         hsMask,
         hbMask,
         nHemiMask,
         sHemiMask,
         allMeow]
mName = ['nh low',
         'sh low',
         'both low',
         'nh mid',
         'sh mid',
         'both mid',
         'nh high',
         'sh high',
         'both high',
         'nh full',
         'sh full',
         'full']

if whatRegion in to_subset:
    for ix in np.arange(len(masks)):
        if np.count_nonzero(masks[ix])>0:
            #print(np.count_nonzero(masks[ix]))
            if False:
                #visualize subsetted regions
                p.figure(figsize=(12,10))
                p.clf()
                p.rcParams['axes.facecolor'] = 'tab:grey'
                p.title(mName[ix])
                rLon,rLat = list(zip(*regions[whatRegion]))
                p.plot(rLon,rLat,'.',alpha = .05)
                p.plot(irLon,irLat,'g*',alpha = .5)
                p.plot(bLon, bLat, "k,",alpha=0.5)
                [p.axhline(y=i,color='blue',linestyle='--') for i in lineList]
                p.plot(irLon[masks[ix]],irLat[masks[ix]],'r.')
                p.tight_layout()
                p.show()
            latSub_latLon = list(zip(irLat[masks[ix]],irLon[masks[ix]]))
            meow_subsets[(whatRegion,mName[ix])]=latSub_latLon
            meCount[(whatRegion,mName[ix])] = len(irLon[masks[ix]])
else:
    latSub_latLon = list(zip(irLat[allMeow],irLon[allMeow]))
    meow_subsets[(whatRegion,'full')]=latSub_latLon
    meCount[(whatRegion,'full')] = len(irLon[allMeow])

np.savez('fixed_regional_meow_subsets.npz',meCount = meCount, meow_subsets = meow_subsets)
