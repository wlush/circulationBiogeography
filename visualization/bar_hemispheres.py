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
    #return(1.96*sqr)
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
nhFull = bothRes.xs(('global','nh full'),level=(2,3))
shFull = bothRes.xs(('global','sh full'),level=(2,3))

pldArr = np.array([3,15,30,45])
seasons = ['Jan-Mar','Apr-Jun','Jul-Sep','Oct-Dec']
hatching = ['///','..','\\\\','oo']
wide = 2
width = 0.0
posArr = np.array([-1.5*wide,-.5*wide,.5*wide,1.5*wide])
pDict = dict(zip(seasons,posArr))
hDict = dict(zip(seasons,hatching))

fig = p.figure(1,figsize=(8,10), constrained_layout=True)
p.clf()
p.rcParams['axes.facecolor'] = 'white'
ax1 = fig.add_subplot(321)
ax1.set_title('Northern Hemisphere')
for season in seasons:
    plotArr = []
    numArr=[]
    errArr = []
    pos = pDict[season]
    htch = hDict[season]
    for ix in pldArr:
        #numArr.append(int(globalFull.loc[season,ix]['total_bounds']))
        errArr.append(nhFull.loc[season,ix]['ci'])
        plotArr.append(nhFull.loc[season,ix]['pct_bounds_hit'])

    #ax1.plot(pldArr,plotArr,label = '%s'%(season))
    
    ax1.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    ax1.errorbar(pldArr+pos,plotArr,yerr=errArr,linestyle='none',color='k',zorder=55)
    width+=wide
    
ax1.axhline(y=.25,linestyle='dashed',color='grey',label = 'random', zorder=5)
ax1.set_ylim([0.0,0.75])
ax1.set(ylabel='fraction of model\nboundaries near MEOW',xticks=pldArr,xticklabels=[])
ax1.legend(loc='upper left',fontsize='small')
p.text(0.95,.9,'A',size='x-large',transform=ax1.transAxes)

ax2 = fig.add_subplot(322)
ax2.set_title('Southern Hemisphere')
for season in seasons:
    plotArr = []
    numArr=[]
    errArr = []
    pos = pDict[season]
    htch = hDict[season]
    for ix in pldArr:
        #numArr.append(int(globalFull.loc[season,ix]['total_bounds']))
        errArr.append(shFull.loc[season,ix]['ci'])
        plotArr.append(shFull.loc[season,ix]['pct_bounds_hit'])
    
    ax2.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    ax2.errorbar(pldArr+pos,plotArr,yerr=errArr,linestyle='none',color='k',zorder=55)
    width+=wide

ax2.axhline(y=.25,linestyle='dashed',color='grey',label = 'random', zorder=5)
ax2.set_ylim([0.0,0.75])
ax2.set(yticklabels=[],xticks=pldArr,xticklabels=[])
p.text(0.025,.90,'B',size='x-large',transform=ax2.transAxes)

ax3 = fig.add_subplot(323)
wide = 2
width = 0.0
for season in seasons:
    pos = pDict[season]
    htch = hDict[season]
    plotArr = []
    for ix in pldArr:
        plotArr.append(nhFull.loc[season,ix]['pct_meow_hit'])
    ax3.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    width+=wide

ax3.set_ylim([0.0,0.8])
ax3.set(xticks=pldArr,xticklabels=[])
ax3.set(ylabel='fraction of MEOW\nboundaries predicted by model',xticks=pldArr,xticklabels=pldArr)
p.text(0.95,.90,'C',size='x-large',transform=ax3.transAxes)

ax4 = fig.add_subplot(324)
wide = 2
width = 0.0
for season in seasons:
    pos = pDict[season]
    htch = hDict[season]
    plotArr = []
    for ix in pldArr:
        plotArr.append(shFull.loc[season,ix]['pct_meow_hit'])
    ax4.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    width+=wide

ax4.set_ylim([0.0,0.8])
ax4.set(xticks=pldArr,xticklabels=[])
ax4.set(yticklabels=[])
p.text(0.025,.90,'D',size='x-large',transform=ax4.transAxes)

ax5 = fig.add_subplot(325)
wide = 2
width = 0.0
for season in seasons:
    pos = pDict[season]
    htch = hDict[season]
    plotArr = []
    for ix in pldArr:
        plotArr.append(nhFull.loc[season,ix]['total_bounds'])
    ax5.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    width+=wide
ax5.set_ylim([0.0,275.])
ax5.set(xlabel='larval duration (days)',xticks=pldArr,xticklabels=pldArr)
ax5.set(ylabel='no. of model boundaries',)
p.text(0.95,.90,'E',size='x-large',transform=ax5.transAxes)

ax6 = fig.add_subplot(326)
wide = 2
width = 0.0
for season in seasons:
    pos = pDict[season]
    htch = hDict[season]
    plotArr = []
    for ix in pldArr:
        plotArr.append(shFull.loc[season,ix]['total_bounds'])
    ax6.bar(pldArr+pos,plotArr,wide,label = '%s'%(season),hatch=htch,edgecolor='k',alpha=.5,zorder=50)
    width+=wide
ax6.set_ylim([0.0,275.])
ax6.set(xlabel='larval duration (days)',xticks=pldArr,xticklabels=pldArr)
ax6.set(yticklabels=[])
p.text(0.025,.90,'F',size='x-large',transform=ax6.transAxes)

p.tight_layout()
p.show(block=False)
p.savefig('modelPerformance_hemispheres.png',dpi=500)
