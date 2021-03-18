print('segs to bbox')
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import box
from shapely.ops import unary_union

def seg_to_bbox(seg):
    npseg = np.array(seg)
    npseg1 = npseg.reshape(npseg.shape[0]//2, 2)
    po = Polygon(npseg1)
    b = box(*po.bounds)
    return b



def segs_to_bbox(segs):
    boxes = [seg_to_bbox(s) for s in segs]
    u = unary_union(boxes)
    return u.bounds




segs = [[0,0,0,1,1,1,0,0],[0,0,0,1,2,2,0,0]]

npseg11 = segs_to_bbox(segs)

# npsegs = np.array(segs)
# print(npsegs.shape)
# a = npsegs.shape[0]//2
# print(a)
# npsegs1 = npsegs.reshape((a, 2))
# print(npsegs1.shape)
# print(npsegs1)
#
#
#
# po = Polygon(npsegs1)
# print(po)
# print(po.bounds)
# print(type(po.bounds))
#
# bbox = list(po.bounds)
# print(bbox)
# # # import