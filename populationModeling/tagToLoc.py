#function to go from a tag to a grid x and y location

import numpy as np
import pylab as p

def tagArr2locs(tag):
    dec = tag/10000.
    nx = dec.astype(int)
    ny = (np.around((dec-nx)*10000)).astype(int)
    return nx,ny
