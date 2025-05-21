import numpy as np
import pylab as p
import netCDF4 as nc
import xarray as xr
import pandas as pd
import geopandas as gpd

from sklearn.neighbors import BallTree,DistanceMetric
import glob

dDir = '/data/guppy/willlush/trm_big_runs/cGrid/Analysis/Popmodel/'
import sys
sys.path.insert(0, dDir) #import modules from /Popmodel directory
import tagToLoc as ttl
import fixOffByOne as fob

caseList = ['Atlantic','norPac','souPac','fulInd','indPac']

# bLon = []
# bLat = []
# for case in caseList:
#     dDir = '/data/guppy/willlush/neutralModelMPI_output/jaccard/'
#     dataName=dDir+'%s_%s_pld%s_withIP_minus3.nc'%(case,'spr',30)

#     data = xr.load_dataset(dataName)
    
#     lonVec=bLon.extend(data["lonVec"].values)
#     latVec=bLat.extend(data["latVec"].values)

# bLon = np.array(bLon)
# bLat = np.array(bLat)

earthRad = 6371 #Earth's radius in km - for computing distances in radians

getCounts = np.load('fixed_regional_meow_subsets.npz',allow_pickle=True)
meCount = getCounts['meCount'].item()
meow_subsets = getCounts['meow_subsets'].item()
for key in meow_subsets.keys():
    meow_subsets[key] = [(round(x[0],7),round(x[1],7)) for x in meow_subsets[key]]

loadPicked = np.load('automated_bounds_regionalSubset_max_allGen.npz',allow_pickle=True)

pCount = loadPicked['pCount'].item()
pick_subsets = loadPicked['pick_subsets'].item()

pldList = [3,15,30,45]
seaList = ['spr','fal','win','sum']
genList = [1000]
genList = [0, 1, 2, 3, 4, 5, 10, 25, 50, 75, 100, 250, 500, 750, 999, 1000]
seaDict = {'spr':'Apr-Jun','fal':'Oct-Dec','win':'Jan-Mar','sum':'Jul-Sep'}

getRegions = np.load('analysis_regions.npz',allow_pickle=True)
regions = getRegions['regions'].item()

rmRegions = ['arctic_archipelago', 'svalbard', 'novaya_zemlya']

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
radLatLon = np.radians(meowLatLon)

# #plotRadius = meanDist*.125 #1/8 mean distance between boundaries...
plotRadius = 153.57 #in km
    
analysis_regions = ['australia','south_america','north_america','africa','asia','europe','atlantic_basin','pacific_basin','indian_basin','mediterranean_sea','gulf_of_mexico_caribbean_sea']
to_subset = ['south_america','north_america','africa','asia','atlantic_basin','pacific_basin','europe']
analysis_regions.append('global')
to_subset.append('global')

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

tpLon,tpLat = list(zip(*toPlot))
nullLatLon = list(zip(tpLat,tpLon))
nullRad = np.radians(nullLatLon)
nullTree = BallTree(nullRad,metric='haversine')

nTest =  nullTree.query_radius(radLatLon,r=153.57/earthRad)

tpLon = np.array(tpLon)
tpLat = np.array(tpLat)

regions['global'] = list(zip(tpLon,tpLat))

meowList = list(zip(mLat,mLon))
#make dictionary of null results per MEOW boundary
nullDict = {}
nLat = []
[nLat.extend(tpLat[nTest[x]]) for x in np.arange(len(nTest))]
nLon = []
[nLon.extend(tpLon[nTest[x]]) for x in np.arange(len(nTest))]

whichSeason = []
whichGen = []
whichPLD = []
whichRegion = []
latSubsection =[]
meowBoundsHit = []
meowBoundsTotal = []
totalBounds = []
totalBounds_inRadius = []
totalPoints = []
pctMeowHit = []
pctPointsHit = []

nullTotalBounds = []
nullBoundsHit = []
pctNullHit = []

for PLD in pldList:
    for season in seaList:
        for gen in genList:
            wG = np.argwhere(np.array(genList)==gen)[0]
            cLon = []
            cLat = []
            cJac = []
            rmList = []

            #set regions...
            for rg in ['global']:
                rgLon,rgLat = list(zip(*regions[rg]))
                rgLon = np.array(rgLon)
                rgLat = np.array(rgLat)
                
                hiLatN = rgLat>=60
                hiLatS = rgLat<=-60
                mdLatN = (rgLat<60)&(rgLat>=30)
                mdLatS = (rgLat>-60)&(rgLat<=-30)
                loLatN = (rgLat<30)&(rgLat>=0)
                loLatS = (rgLat>-30)&(rgLat<=0)
                lo = loLatN | loLatS
                md = mdLatS | mdLatN
                hi = hiLatS | hiLatN
                nh = rgLat>0
                sh = rgLat<0
                full = np.ones(len(rgLat)).astype(bool)

                if rg in to_subset: #subset
                    lat_subsets = {'nh high':hiLatN,'nh mid':mdLatN,'nh low':loLatN,'sh mid':mdLatS,
                                   'sh low':loLatS,'both low':lo,'both mid':md,'nh full':nh,'sh full':sh,'full':full}
                else:
                    lat_subsets = {'full':full}            
                
                for subset in lat_subsets.keys():
                    meKey = (rg, subset)
                    if meKey in meCount.keys():
                        numMeow = meCount[meKey]
                        meow_subLatLon = meow_subsets[meKey]
                        msLat,msLon = list(zip(*meow_subLatLon))
                        tempLatLon = np.radians(meow_subLatLon)

                        #get null values - make balltree to find # boundaries nearby
                        nullLat = rgLat.copy()[lat_subsets[subset]]
                        nullLon = rgLon.copy()[lat_subsets[subset]]
                        nTree = BallTree(np.radians(list(zip(nullLat,nullLon))),metric='haversine')
                        nullInd = nTree.query_radius(tempLatLon,r = plotRadius/earthRad)
                        nIndices = []
                        for ix in nullInd:
                            nIndices.extend(ix)

                        loadTup = (season, PLD, rg, subset,gen)
                    elif rg =='global':
                        loadTup = None
                        
                    if loadTup in pCount.keys():
                        #fix season issue
                        test = [((sea, PLD, rg, subset) in pCount.keys())  for sea in seaList]
                        if pCount[loadTup]==0:
                            counter = 0
                            indices = []
                        else:
                            nPicked_inRegion = pCount[loadTup]
                            pick_latLon = pick_subsets[loadTup]
                            pLat,pLon = list(zip(*pick_latLon))

                            ctLon = np.array(pLon)
                            ctLat = np.array(pLat)
                            cZip = np.radians(list(zip(ctLat,ctLon)))
                            cTree = BallTree(cZip,metric='haversine')
                            
                            ind = cTree.query_radius(tempLatLon,r = plotRadius/earthRad)
                            counter = 0
                            indices = []
                            for ix in ind:
                                if len(ix)>0:
                                    counter+=1
                                    indices.extend(ix)

                        cIndices = np.unique(indices)
                        cCount = len(cIndices)
                        
                        meowBoundsHit.append(counter)
                        meowBoundsTotal.append(numMeow)
                        totalBounds.append(nPicked_inRegion)
                        totalBounds_inRadius.append(cCount)
                        whichSeason.append(seaDict[season])
                        whichGen.append(gen)
                        whichPLD.append(PLD)
                        totalPoints.append(nPicked_inRegion)
                        whichRegion.append(rg)
                        latSubsection.append(subset)
                        pctMeowHit.append(counter/numMeow)
                        pctPointsHit.append(cCount/nPicked_inRegion)

                        nullTotalBounds.append(len(nullLon))
                        nullBoundsHit.append(len(nIndices))
                        pctNullHit.append(len(nIndices)/len(nullLon))

master_stats = pd.DataFrame({'season':whichSeason,
                             'pld':whichPLD,
                             'generation':whichGen,
                             'region':whichRegion,
                             'lat_subset':latSubsection,
                             'null_bounds_total':nullTotalBounds,
                             'null_bounds_hit':nullBoundsHit,
                             'meow_bounds_hit':meowBoundsHit,
                             'total_bounds':totalBounds,
                             'total_bounds_hit':totalBounds_inRadius,
                             'pct_null_hit':pctNullHit,
                             'pct_meow_hit':pctMeowHit,
                             'pct_bounds_hit':pctPointsHit,
                             'total_meow_bounds':meowBoundsTotal,})

#master_stats.to_pickle('automated_regional_dbscanCent_stats.pkl')
#master_stats.to_pickle('automated_centroid_multiGen.pkl')
master_stats.to_pickle('automated_max_multiGen.pkl')
