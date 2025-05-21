import numpy as np
import pylab as p
import netCDF4 as nc
import xarray as xr
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as ftr
import matplotlib.colors as mcolors

from sklearn.neighbors import BallTree,DistanceMetric
import glob

dDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/'

#confidence interval (from https://stats.stackexchange.com/questions/156796/how-to-build-a-confidence-interval-with-only-binary-test-results)
def confInt(numSuccess,numSamples):
    pctSuccess = numSuccess/numSamples
    numerator = pctSuccess*(1.-pctSuccess)
    sqr = np.sqrt(numerator/numSamples)
    #return(1.96*sqr) #95% CI
    return(1.645*sqr)

#from https://online.stat.psu.edu/statprogram/reviews/statistical-concepts/proportions
def z_test(n_success1,n_total1,n_success2,n_total2):
    pHat1 = n_success1/n_total1
    pHat2 = n_success2/n_total2
    pTot =  (n_success1+n_success2)/(n_total1+n_total2)
    zDenom = pTot*(1.0-pTot)*((1/n_total1)+(1/n_total2))

    zStat = (pHat1-pHat2)/np.sqrt(np.abs(zDenom))
    return(np.abs(zStat))

get_stats = pd.read_pickle(dDir+'automated_max_multiGen.pkl')

sigLev = 1.645 #z-statistic value for p=.05
sigLev2 = 1.282 #z-statistic value for p=.1
get_stats = get_stats[get_stats['generation']==1000]
get_stats.drop(['generation'],axis=1,inplace=True)

get_stats.set_index(['season', 'pld', 'region', 'lat_subset'],inplace=True)

bothRes = get_stats.copy()

bothRes['ci'] = bothRes.apply(lambda x: confInt(x['total_bounds_hit'], x['total_bounds']), axis=1)
#bothRes['ci'] = bothRes.apply(lambda x: z_test(x['total_bounds_hit'], x['total_bounds'],x['null_bounds_hit'],x['total_bounds']), axis=1)
globalFull = bothRes.xs(('global','full'),level=(2,3))

pldArr = np.array([3,15,30,45])
seasons = ['Jan-Mar','Apr-Jun','Jul-Sep','Oct-Dec']
hatching = ['///','..','\\\\','oo']

fig = p.figure(figsize=(8,10), constrained_layout=True)
p.clf()
p.rcParams['axes.facecolor'] = 'white'
#fig.suptitle('Global Model Performance', fontsize=16)
ax1 = fig.add_subplot(211)
wide = 2
width = 0.0
posArr = np.array([-1.5*wide,-.5*wide,.5*wide,1.5*wide])
pDict = dict(zip(seasons,posArr))
hDict = dict(zip(seasons,hatching))
for season in seasons:
    plotArr = []
    numArr=[]
    errArr = []
    pos = pDict[season]
    htch = hDict[season]
    for ix in pldArr:
        #numArr.append(int(globalFull.loc[season,ix]['total_bounds']))
        errArr.append(globalFull.loc[season,ix]['ci'])
        plotArr.append(globalFull.loc[season,ix]['pct_bounds_hit'])

    #ax1.plot(pldArr,plotArr,label = '%s'%(season))
    
    ax1.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    ax1.errorbar(pldArr+pos,plotArr,yerr=errArr,linestyle='none',color='k',zorder=55)
    width+=wide
    
ax1.axhline(y=.25,linestyle='dashed',color='grey',label = 'random', zorder=5)
ax1.set_ylim([0.0,0.5])
#ax1.set_xticks([])#,xticklabels=[])
ax1.set(ylabel='fraction of model boundaries\nnear MEOW boundaries',xticks=[],xticklabels=[])
ax1.legend(loc='upper left')
p.text(0.95,.925,'A',size='x-large',transform=ax1.transAxes)

ax2 = fig.add_subplot(212)
wide = 2
width = 0.0
for season in seasons:
    pos = pDict[season]
    htch = hDict[season]
    plotArr = []
    for ix in pldArr:
        plotArr.append(globalFull.loc[season,ix]['pct_meow_hit'])
    #ax2.bar(pldArr+pos,plotArr,wide,label = '%s'%(season))
    ax2.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    width+=wide

ax2.set_ylim([0.0,0.8])
#ax2.legend(loc=1,ncol=1)
ax2.set(xlabel='larval duration (days)',xticks=pldArr,xticklabels=pldArr)
ax2.set(ylabel='fraction of MEOW boundaries predicted\nby model',xticks=pldArr,xticklabels=pldArr)
p.text(0.95,.925,'B',size='x-large',transform=ax2.transAxes)

p.tight_layout()
p.show(block=False)
p.savefig('modelPerformance_global.png',dpi=500)
