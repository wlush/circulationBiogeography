import pylab as p
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as ftr
import glob
import matplotlib.patches as mpatches

#What directory to get data from
dDir = '/data/guppy/willlush/neutralModelMPI_output/'
dataDir=dDir+'Atlantic_data_season_spr_PLD30_cPer10/'

#read in data, sort, and read in
allFileNames=glob.glob(dataDir+'*[0123].nc')
allFileNames=glob.glob(dataDir+'*.nc')
allFileNames=sorted(allFileNames)
data=xr.open_mfdataset(allFileNames,combine='nested',concat_dim='gen',chunks={'nSpecies':100})

lonVec=data["lonVec"].values
latVec=data["latVec"].values

#subregion
figsize=(9,10)
minLon=-78.0; maxLon=-60.0
minLat=35.0; maxLat=47.0
axisVec=(minLon,maxLon,minLat,maxLat)

ind = [9188, 9339, 8965] #indices of start locations...
fgenList = data['gen'].values
genList = [0,10,100,1000]
whereInGL = [np.argwhere(fgenList==x).item() for x in genList]

th = .001
fig = p.figure(figsize=(8,6),layout='constrained')
p.clf()
prop_cycle = p.rcParams['axes.prop_cycle']
colorList = prop_cycle.by_key()['color']
pSpec = [221,222,223,224]
for ix in np.arange(4):
    
    genInd = whereInGL[ix]
    wGen = genList[ix]
    ax = fig.add_subplot(pSpec[ix],projection=ccrs.PlateCarree())
    ax.add_feature(ftr.LAND,facecolor='tab:grey',alpha=.5)
    ax.add_feature(ftr.COASTLINE,linewidth=0.3)
    ax.set_extent(axisVec,crs=ccrs.PlateCarree())

    for jx in np.arange(len(ind)):
        co = colorList[jx]
        j = ind[jx]
        popData = data['popMatrix'][genInd,j,:].values.copy()
        pdMask = popData>th
        
        if ix==0:
            ax.set_title('Generation %s (initial patches)'%(wGen))
            ax.plot(lonVec[pdMask],latVec[pdMask],'*',color=co,markersize=15,)
            #ax.text(.975,0.05,'', transform=ax.transAxes,va='bottom',ha='right')
            #ax.text(.025,.975,tt,transform=ax.transAxes,va='top',fontsize='large')
        else:
            ax.set_title('Generation %s'%(wGen))
            #ax.text(0.025,.975,tt,transform=ax.transAxes,va='top',fontsize='large')
            if j==ind[0]:
                if ix==3:
                    ax.plot(lonVec[pdMask]
                            ,latVec[pdMask],
                            '.',color=co,alpha = 1,
                            zorder = 100,label='model spp. 1')
                else:
                    ax.plot(lonVec[pdMask],
                            latVec[pdMask],
                            '.',color=co,alpha = 1,
                            zorder = 100)
                if len(lonVec[pdMask])>0:
                    eA = np.argmax(lonVec[pdMask])
                    eB = np.argmin(lonVec[pdMask])
                    ax.arrow(x=lonVec[pdMask][eA],
                             y=latVec[pdMask][eA],
                             dx=1,dy=-1.2,zorder = 95,
                             color=co,linestyle=(5,(2,3.5)))
                    ax.arrow(x=lonVec[pdMask][eB],
                             y=latVec[pdMask][eB],
                             dx=1,dy=-1.2,zorder = 95,
                             color=co,linestyle=(5,(2,3.5)))
            elif j==ind[1]:
                if ix==3:
                    ax.plot(lonVec[pdMask],
                            latVec[pdMask],
                            'o',color=co,
                            label='model spp. 2')
                else:
                    ax.plot(lonVec[pdMask],
                            latVec[pdMask],
                            'o',color=co)
                eMsk = latVec[pdMask]<44.
                eA = np.argmax(lonVec[pdMask][eMsk])
                eB = np.argmin(latVec[pdMask])
                if ix==2:
                    eB = np.argmin(lonVec[pdMask])
                if ix==1:
                    tx = lonVec[pdMask][eMsk][eA]+1.0
                    ty = latVec[pdMask][eMsk][eA]-1.2
                    arr = mpatches.FancyArrowPatch((lonVec[pdMask][eMsk][eA],
                                                    latVec[pdMask][eMsk][eA]),
                                                   (tx, ty),color=co,linestyle=(5,(2,3.5)))

                    ax.add_patch(arr)
                    ax.annotate("range edges\nshown as dashed lines",(1.5,-0.1), xycoords=arr,color='k',ha='center', va='top')
                else:
                    ax.arrow(x=lonVec[pdMask][eMsk][eA],
                             y=latVec[pdMask][eMsk][eA],
                             dx=1,dy=-1.2,color=co,
                             linestyle=(5,(2,3.5)))
                ax.arrow(x=lonVec[pdMask][eB],
                         y=latVec[pdMask][eB],
                         dx=1,dy=-1.2,color=co,
                         linestyle=(5,(2,3.5)))

            elif j==ind[2]:
                if ix==3:
                    ax.plot(lonVec[pdMask],
                            latVec[pdMask],
                            '.',alpha = .75,
                            color=co,label='model spp. 3')
                else:
                    ax.plot(lonVec[pdMask],
                            latVec[pdMask],
                            '.',color=co,alpha = .75)
                eA = np.argmax(latVec[pdMask])
                eB = np.argmin(latVec[pdMask])
                ax.arrow(x=lonVec[pdMask][eA],
                         y=latVec[pdMask][eA],
                         dx=1,dy=-1.2,color=co,
                         linestyle=(5,(2,3.5)))
                ax.arrow(x=lonVec[pdMask][eB],
                         y=latVec[pdMask][eB],
                         dx=1,dy=-1.2,color=co,
                         linestyle=(5,(2,3.5)))

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles,labels,loc='lower right')
p.savefig('3spp_alongshore.png',dpi=500)
p.show()
