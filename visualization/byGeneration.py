import numpy as np
import pylab as p
import netCDF4 as nc
import xarray as xr
import pandas as pd
#import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as ftr
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go

from sklearn.neighbors import BallTree,DistanceMetric
import glob

#dDir = '/data/guppyhome/willlush/workfiles/trm_big_runs/analysisCode/analysisFromJamie/'
dDir = '/data/breakhome/willlush/workfiles/trm_big_runs/analysisCode/neutralModelPaper_analysis/'

def z_test(n_success1,n_total1,n_success2,n_total2):
    pHat1 = n_success1/n_total1
    pHat2 = n_success2/n_total2
    pTot =  (n_success1+n_success2)/(n_total1+n_total2)
    zDenom = pTot*(1.0-pTot)*((1/n_total1)+(1/n_total2))

    zStat = (pHat1-pHat2)/np.sqrt(np.abs(zDenom))
    return(zStat)

get_stats_top = pd.read_pickle(dDir+'automated_max_multiGen.pkl')

pldArr = [3,15,30,45]
seasons = ['Jan-Mar','Apr-Jun','Jul-Sep','Oct-Dec']
#genList = np.array([0, 1, 2, 3, 4, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000])
genList = np.array([100, 250, 500, 750, 1000])

sigLev = 1.645 #z-statistic value for p=.05
sigLev2 = 1.282 #z-statistic value for p=.1

fig = p.figure(figsize=(6.,6.),layout='constrained')
p.clf()
#p.rcParams['axes.facecolor'] = 'white'
#fig.suptitle('Global Model Performance', fontsize=16)
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

#for season in seasons:
season = seasons[1]
for ix in pldArr:
    boundsHit = []
    meowHit = []
    numBounds=[]
    for gen in genList:
        get_stats = get_stats_top[get_stats_top['generation']==gen].copy()
        get_stats.drop(['generation'],axis=1,inplace=True)

        get_stats.set_index(['season', 'pld', 'region', 'lat_subset'],inplace=True)
        
        bothRes = get_stats.copy()
        
        bothRes['z_stat'] = bothRes.apply(lambda x: z_test(x['total_bounds_hit'], x['total_bounds'],x['null_bounds_hit'],x['null_bounds_total']), axis=1)
        globalFull = bothRes.xs(('global','full'),level=(2,3))
        boundsHit.append(globalFull.loc[season,ix]['pct_bounds_hit'])
        meowHit.append(globalFull.loc[season,ix]['pct_meow_hit'])
        numBounds.append(int(globalFull.loc[season,ix]['total_bounds']))
        #gL.append(globalFull.loc[season,30]['pct_bounds_hit'])

    ax1.plot(genList,boundsHit,'o-',markersize=4,label = '%s'%(ix))
    ax1.set_ylabel('% bounds near MEOW')
    #ax1.legend(loc='upper left',title='pld')
    ax1.set_ylim([.20,.40])
    ax1.set_xticks([])
    p.text(0.95,.85,'A',size='large',transform=ax1.transAxes)
    
    ax2.plot(genList,meowHit,'o-',markersize=4)
    ax2.set_ylabel('% MEOW predicted')
    ax2.set_ylim([.20,.70])
    ax2.set_xticks([])
    p.text(0.95,.85,'B',size='large',transform=ax2.transAxes)
    
    ax3.plot(genList,numBounds,'o-',markersize=4,)
    ax3.set_ylabel('# boundaries')
    ax3.set_xlabel('generation')
    ax3.set_ylim([100,500])
    p.text(0.95,.85,'C',size='large',transform=ax3.transAxes)
    
ax1.axhline(.25,color='grey',linestyle='dashed',label='expected from\nrandom')
# ax2.axhline(.25,color='grey',linestyle='dashed',alpha=0)
# ax2.legend(, )
handles, labels = ax1.get_legend_handles_labels()
lgd = fig.legend(handles, labels,loc='center left', bbox_to_anchor=(1.01, .5),bbox_transform=fig.transFigure,title='PLD')
fig.suptitle('%s larval releases'%(season))
fig.tight_layout()
p.savefig('performance_byGeneration.png', bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=500)
p.show()
