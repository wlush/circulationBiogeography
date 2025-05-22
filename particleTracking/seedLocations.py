#Uses landmask on t-points to find seeding locations within a given geographic
#location. Adapted from previous Mercator A-grid seeding location scripts
#Can return either an ascii file or a mask (MASK HAS YET TO BE IMPLEMENTED
# CORRECTLY WITH SUBGRID IN TRACMASS - 11/7)
# Created 11/7/2018 wgl

import pylab as p
import numpy as np
import netCDF4 as nc
from scipy import ndimage as ndi

#-------------------------------------------------------------------------------
#Data locations and input/output options
#!!!!! DATA OUTPUT LOCATION WILL CHANGE WHEN I ORGANIZE CODE !!!!!

#Data directory:
inDataDir = '/data/guppy2/willlush/Mercator/cGrid/trmSymlinks/'
maskFile = 'Mask.nc'

maskIn = inDataDir+maskFile

#Output directory:
#CHANGE WHEN DIRECTORY CHANGES!!! 11/7
outDataDir = '/data/guppy/willlush/trm_big_runs/cGrid/Runs/seedfiles/'
oDDSuf = '.seed'
#Name for seedfile:
#seedFile = 'Atlantic'
#seedFile = 'norPac'
#seedFile = 'souPac'
#seedFile = 'indPac'
#seedFile = 'fulInd'
#seedFile = 'antArc'
seedFile = 'testTiming'

seedOut = outDataDir+seedFile+oDDSuf

#options for script
makeDomain = False #plots nxmax and nxmin of prev. runs
plotDomain = False #plots overall seeding domain 
plotSeedLocs = False #plots final seeding locations
manual = True

####DO YOU WANT TO SAVE????!?!?#####
saveFile = True #saves output to file

#---------------------------------------------------------------------------
# depth at which particles whould be released...
#this is slightly more complicated, and depends on TRM setup

#WGL use case - 36 depth levels, where 36 is the surface:
depBelow = 1 #depth levels below surface

#---------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#Load in mask file - use landmask at t points...
oMask = nc.Dataset(maskIn,'r')
#msk = oMask['tmask'][0,:,:,:].data #mask shape is 50,3059,4320 (so z,y,x)
msk = oMask['tmask'][0,0,:,:].data.astype(bool)
oMask.close()

#pick points manually:
if manual == True:
    testX = np.arange(2556,2728)
    testY = np.full(len(testX),2025)
    p.figure(1,figsize=(9.0,9.0))
    p.clf()
    p.imshow(msk,cmap = 'Greys',alpha = .2,origin = 'lower')
    p.plot(testX,testY,'b.')
    p.show()

    
    if saveFile == False:
        assert False
    else:
        SPGridx = testX
        SPGridy = testY

if manual == False:
    #---------------------------------------------------------------------------
    #Overall Locations - quadrilaterals containing release points
    # LOCATIONS ARE IN GRID SPACE
    #fgXmin,fgXmax = 0,msk.shape[2]
    #fgYmin,fgYmax = 0,msk.shape[1]

    if True: #Full globe
        nxMin = 0
        nxMax = msk.shape[1]
        nyMin = 0
        nyMax = msk.shape[0]

    if False: #East Coast North America (Nova Scotia to Florida)
        nxMin = 2464
        nxMax = 2736
        nyMin = 1804
        nyMax = 2128

    if False: #Full Atlantic
        nyMin = 670 #south of Tierra del Fuego
        nyMax = msk.shape[0]
        nxMin = 2260
        nxMax = 3950

    if False: #North Pacific
        nyMin = 1360 #south of equator
        nyMax = msk.shape[0]
        nxMin = 370
        nxMax = 2530

    if False: #South Pacific
        nyMin = 580 
        nyMax = 1590 #north of Borneo
        nxMin = 370
        nxMax = 2780

    if False: #Indo-Pacific
        nyMin = 980 #Between Australia and Tasmania
        nyMax = 1810 #north of Taiwan
        nxMin = 120 #East of Sri Lanka
        nxMax = 1320

    if False: #Indian Ocean - special case
        nyMin = 580 
        nyMax = 1940
        nxMin = 0
        nxMax = 4320

    if False: #Southern Ocean
        nyMin = 0 
        nyMax = 670
        nxMin = 0
        nxMax = 4320

    if makeDomain == True:

        #Atlantic - Blue
        atXmax,atXmin = 3950,2260
        atYmax,atYmin = msk.shape[1],670
        atX,atY = [atXmax,atXmin],[atYmax,atYmin]
        atl = 'Blue'

        #North Pacific - Green
        npXmax,npXmin = 2530, 370
        npYmax,npYmin = msk.shape[1], 1360
        npX,npY = [npXmax,npXmin],[npYmax,npYmin]
        nor = 'Green'

        #South Pacific - Red
        spXmax,spXmin = 2780, 370
        spYmax,spYmin = 1590, 580
        spX,spY = [spXmax,spXmin],[spYmax,spYmin]
        sou = 'Red'

        #Indo-Pacific - Cyan
        ipXmax,ipXmin = 1320, 120
        ipYmax,ipYmin = 1810, 980
        ipX,ipY = [ipXmax,ipXmin],[ipYmax,ipYmin]
        ind = 'Cyan'

        xArr = np.arange(msk.shape[2])
        yArr = np.arange(msk.shape[1])

        #plots surface landmask
        p.figure(1,figsize=(10.0,8.0))
        p.clf()
        p.pcolormesh(msk[0,fgYmin:fgYmax,fgXmin:fgXmax])
        #atlantic
        for at in atX:
            p.plot(np.full(yArr.shape,at),yArr,color = atl)
        for at in atY:
            p.plot(xArr,np.full(xArr.shape,at),color = atl)

        #north pacific
        for no in npX:
            p.plot(np.full(yArr.shape,no),yArr,color = nor)
        for no in npY:
            p.plot(xArr,np.full(xArr.shape,no),color = nor)
        p.show()

        #south pacific
        for so in spX:
            p.plot(np.full(yArr.shape,so),yArr,color = sou)
        for so in spY:
            p.plot(xArr,np.full(xArr.shape,so),color = sou)
        p.show()

        #indopacific
        for so in ipX:
            p.plot(np.full(yArr.shape,so),yArr,color = ind)
        for so in ipY:
            p.plot(xArr,np.full(xArr.shape,so),color = ind)
        p.show()

        assert False

    #plot domain overview
    if plotDomain == True:
        #plots surface landmask
        p.figure(1,figsize=(9.0,9.0))
        p.clf()
        p.pcolormesh(msk[0,nyMin:nyMax,nxMin:nxMax])
        p.show()
    #---------------------------------------------------------------------------
    #binary decomposition - getting grid points for seeding

    #generate binary footprint:
    foot = ndi.generate_binary_structure(2,1)

    #binary erosion - two binary erosion steps to get two coast-adjacent points
    erode = ndi.binary_erosion(msk[depBelow,nyMin:nyMax,nxMin:nxMax],foot,border_value=1)
    erode2 = ndi.binary_erosion(erode,foot,border_value=1)
    edge = msk[depBelow,nyMin:nyMax,nxMin:nxMax] ^ erode2

    #---------------------------------------------------------------------------
    #Deselect points manually:
    #Use plot domain overview to look at points to remove -> comment to which domain
    # your exclusions correspond
    #NOTE - these are relative to subsetted domain, not full!

    if False: #for East Coast North America
        zone_1 = {'nxMin':25,'nxMax':62,'nyMin':0,'nyMax':30} #bahamas
        zone_2 = {'nxMin':198,'nxMax':206,'nyMin':99,'nyMax':105} #Bermuda
        zone_3 = {'nxMin':263,'nxMax':269,'nyMin':266,'nyMax':288} #Sable Island
        zones = [zone_1,zone_2,zone_3]
        for zone in zones:
            edge[zone['nyMin']:zone['nyMax'],zone['nxMin']:zone['nxMax']] = 0

    if False: #for Atlantic
        zone_1 = {'nxMin':0,'nxMax':350,'nyMin':315,'nyMax':915} #WC SAm.
        zone_2 = {'nxMin':0,'nxMax':116,'nyMin':760,'nyMax':1038} #WC centAm. 1
        zone_3 = {'nxMin':0,'nxMax':175,'nyMin':870,'nyMax':987} #WC centAm. 2
        zone_4 = {'nxMin':0,'nxMax':246,'nyMin':900,'nyMax':929} #WC centAm. 3
        zone_5 = {'nxMin':0,'nxMax':185,'nyMin':925,'nyMax':940} #WC centAm. 4
        zone_6 = {'nxMin':220,'nxMax':241,'nyMin':920,'nyMax':934} #WC centAm. 5
        zone_7 = {'nxMin':1569,'nxMax':1690,'nyMin':988,'nyMax':1206} #Red Sea
        zones = [zone_1,zone_2,zone_3,zone_4,zone_5,zone_6,zone_7]
        for zone in zones:
            edge[zone['nyMin']:zone['nyMax'],zone['nxMin']:zone['nxMax']] = 0

    if False: #for North Pacific
        zone_1 = {'nxMin':1929,'nxMax':2160,'nyMin':351,'nyMax':1699} #EC Nor. Am.
        zone_2 = {'nxMin':1897,'nxMax':1930,'nyMin':360,'nyMax':500} #edge GOMex.
        zone_3 = {'nxMin':2006,'nxMax':2153,'nyMin':298,'nyMax':354} #EC centAm. 1
        zone_4 = {'nxMin':2071,'nxMax':2144,'nyMin':244,'nyMax':300} #EC centAm. 2
        zone_5 = {'nxMin':2138,'nxMax':2160,'nyMin':229,'nyMax':246} #EC centAm. 3
        zone_6 = {'nxMin':2085,'nxMax':2107,'nyMin':239,'nyMax':245} #EC centAm. 4
        zone_7 = {'nxMin':2066,'nxMax':2071,'nyMin':262,'nyMax':285} #EC centAm. 5
        zones = [zone_1,zone_2, zone_3,zone_4,zone_5,zone_6,zone_7]
        for zone in zones:
            edge[zone['nyMin']:zone['nyMax'],zone['nxMin']:zone['nxMax']] = 0

    if False: #for South Pacific
        zone_1 = {'nxMin':2075,'nxMax':2126,'nyMin':1000,'nyMax':1009} #CM
        zone_2 = {'nxMin':2350,'nxMax':2410,'nyMin':960,'nyMax':1009} #Caribbean
        zones = [zone_1,zone_2]
        for zone in zones:
            edge[zone['nyMin']:zone['nyMax'],zone['nxMin']:zone['nxMax']] = 0

    if False: #for Indo-Pacific
        zone_1 = {'nxMin':1060,'nxMax':1150,'nyMin':0,'nyMax':80} #New Zealand
        zones = [zone_1,]
        for zone in zones:
            edge[zone['nyMin']:zone['nyMax'],zone['nxMin']:zone['nxMax']] = 0

    if False: #for Indian Ocean
        zone_1 = {'nxMin':720,'nxMax':3670,'nyMin':0,'nyMax':1360} #Pacific
        zone_2 = {'nxMin':332,'nxMax':3670,'nyMin':980,'nyMax':1360} #Chunk IP
        zone_3 = {'nxMin':363,'nxMax':3670,'nyMin':867,'nyMax':1360} #Chunk IP
        zone_4 = {'nxMin':444,'nxMax':3670,'nyMin':820,'nyMax':1360} #Chunk IP
        zone_5 = {'nxMin':312,'nxMax':3670,'nyMin':1014,'nyMax':1360} #Chunk IP
        zone_6 = {'nxMin':324,'nxMax':3670,'nyMin':995,'nyMax':1360} #Chunk IP
        zone_7 = {'nxMin':341,'nxMax':3670,'nyMin':920,'nyMax':1360} #Chunk IP
        zone_8 = {'nxMin':392,'nxMax':3670,'nyMin':844,'nyMax':1360} #Chunk IP
        zone_9 = {'nxMin':395,'nxMax':3670,'nyMin':833,'nyMax':1360} #Chunk IP
        zone_10 = {'nxMin':425,'nxMax':3670,'nyMin':830,'nyMax':1360} #Chunk IP
        zone_11 = {'nxMin':675,'nxMax':3670,'nyMin':810,'nyMax':1360} #Chunk IP
        zone_12 = {'nxMin':3670,'nxMax':3880,'nyMin':1300,'nyMax':1360} #Med Sea
        zone_13 = {'nxMin':3670,'nxMax':3680,'nyMin':1297,'nyMax':1301} #Med Sea
        zone_14 = {'nxMin':309,'nxMax':314,'nyMin':120,'nyMax':128}
        zones = [zone_1,zone_2,zone_3,zone_4,zone_5,zone_6,zone_7,zone_8,zone_9,
                 zone_10,zone_11,zone_12,zone_13,zone_14]
        for zone in zones:
            edge[zone['nyMin']:zone['nyMax'],zone['nxMin']:zone['nxMax']] = 0

    else:
        zones = None

    #plots seeding locations
    if plotSeedLocs == True:
        p.figure(2,figsize=(9.0,9.0))
        p.clf()
        p.pcolormesh(edge)
        p.show()

    #get seed locations, place on larger grid
    seedPoints = np.nonzero(edge)
    SPGridy = seedPoints[0]+nyMin+1 #remember, y is first here...
    SPGridx = seedPoints[1]+nxMin+1

#-------------------------------------------------------------------------------
#Create and save out ascii file:

if saveFile == True:
    seed = open(seedOut,'w+')

    depth = 36 - depBelow
    isec = 4
    idir = 0

    i_arr = SPGridx
    j_arr = SPGridy
    #length = i_arr.shape[0]

    #for num in np.arange(length):
    for num in np.arange(len(i_arr)):
        i,j = i_arr[num],j_arr[num]
        #print('%6s%6s%6s%6s%6s\n' %(i,j,depth,isec,idir))
        seed.write('%6s%6s%6s%6s%6s\n' %(i,j,depth,isec,idir))

    seed.close
