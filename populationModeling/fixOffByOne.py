#fixes off-by-one error from ij2tag so I don't have to keep typing this out...
import numpy as np
import pylab as p

import tagToLoc as ttl

def fixTags(tagArr):
    tx,ty = ttl.tagArr2locs(tagArr)
    tx = tx-1
    ty = ty-1
    tx[tx==4320]=0
    back2tags = tx*10000+ty
    return(back2tags)

def fixXY(xArr,yArr):
    newX = xArr-1
    newY = yArr-1
    newX[newX==4320]=0
    return(newX,newY)

