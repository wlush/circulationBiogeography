#Combine partial connectivity matrices to form larger connectivity matrix
#from time_cm_combine.py

#!!!!! CURRENT VERSION AS OF 1/25/2019 !!!!!

# ASSUMES THAT MATRICES ARE IN COUNTS, RATHER THAN IN PERCENTAGES
# Assumes that all .npz matrices are in the same directory
# current iteration assumes that all matrices are the same size
# (although it checks this) - future iterations may deal with subsetted matrices

import os
import numpy as np
import pylab as p
from scipy.sparse import csr_matrix #cms saved as csr sparse matrices

#get filenames for all partial conn. matrices (cms) in directory
# Assumes cms are stored as .npz files
# Also assumes that the only npz files in the directory are cm files
# part.npz denotes partial cms
#case = 'Atlantic'
#case = 'norPac'
#case='souPac'
#case = 'fulInd'
case = 'indPac'
years = list(range(2007,2018)) #list from 2007 to 2017
season = 4#nh seasons; 1 is spring, 2 is summer, 3 is fall, 4 is winter


PLD = '45' #'30' #'3' #'15'
compPer = '20' #'10' # '1' #'6'
workPath = '/data/guppy/willlush/conn_matrices/cGrid/'+case+'/'

file_namelist = []
for year in years:
     inDir = workPath+case+str(year)+'_PLD'+PLD+'_c'+compPer+'_PCM'
     temp_namelist = [inDir+'/'+f for f in os.listdir(inDir) if f.endswith('PCM.npz')]
     file_namelist+=temp_namelist
     
cm_namelist = []

if season == 1: #spring
     mos = ['04','05','06']
     ssn = 'spr'
elif season == 2: #summer
     mos = ['07','08','09']
     ssn = 'sum'
elif season ==3: #fall
     mos = ['10','11','12']
     ssn = 'fal'
elif season == 4: #winter
     mos = ['01','02','03']
     ssn = 'win'
else:
     print('invalid season option!')
     assert False

for mo in mos:
    mStr = '_'+mo+'_'
    for name in file_namelist:
        if mStr in name:
            cm_namelist+=[name]

#OUTFILE NAME - MAKE DESCRIPTIVE!!!
outFile = '%s_%s_%s_%s'%(case,ssn,PLD,compPer) #ssn is season
outDir = 'comb%s_PLD%s_c%s/'%(case,PLD,compPer)

if os.path.isdir(workPath+outDir):
    print('directory exists!',outDir)
    outPath = workPath+outDir
else:
    print('creating new directory:',outDir)
    outPath = workPath+outDir
    os.mkdir(outPath)

print(outFile)
assert True
cm_name = outPath+outFile

#Takes first cm to define shape and locations
first = np.load(cm_namelist[0],allow_pickle=True)
fcm = first['cm'].item().astype(np.int16)
test = fcm.todense()
cm_shape = np.shape(test)
assert cm_shape[0]==cm_shape[1], 'CONNECTIVITY MATRIX IS NOT SQUARE'

#initializes a blank connectivity matrix from shape
#cm_total = np.zeros(cm_shape) #total connectivity matrix
cm_total = fcm
#row_count = np.zeros(cm_shape[0])
rowCount = first['relCount']

for name in cm_namelist:
    temp = np.load(name,allow_pickle=True)
    ij2tag = temp['ij2tag']
    tag2ij = temp['tag2ij'].item()
    cm_total = cm_total + temp['cm'].item().astype(np.int16)
    rowCount += temp['relCount']


rawCountsCM = cm_total
ind = rawCountsCM.nonzero()
indi = ind[0]
indj = ind[1]
#create new rowcount for each element (CAREFUL!!!)
invCount=[1.0/rowCount[indi[n]] for n in range(len(indi))]
divSparse=csr_matrix((invCount,(indi,indj)),shape=(rawCountsCM.shape[0],rawCountsCM.shape[1]))
percCM = rawCountsCM.multiply(divSparse)
#cm_nan_fix = np.nan_to_num(perc_cm) #resolved with sparse matrices

assert np.amax(percCM.sum(axis=0)) <= 1, 'Counts are off, check PCM'
assert True #testing cwgl 6/20/2019


if  True: #save the total connectivity matrix
    np.savez(cm_name,
             cm = percCM,
             cm_raw = rawCountsCM,
             ij2tag = ij2tag,
             tag2ij = tag2ij,
             rc = rowCount)

if False: #visualize connectivity matrix
    p.figure(1)
    p.clf()
    p.imshow(np.log10(perc_cm))
    p.show()
    
if False:
    p.figure(2)
    p.clf()
    p.scatter(np.arange(cm_shape[0]),row_count)
    p.show()
