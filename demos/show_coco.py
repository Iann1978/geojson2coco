print('hello this is a demo to show coco data')

from pycocotools.coco import COCO
from pycocotools.mask import encode,decode,area,toBbox

dataDir=r'G:\datasets\coco\2017'
dataType='val2017'
annFile='{}/annotations/instances_{}.json'.format(dataDir, dataType)

coco = COCO(annFile)

print(coco)

imgIds = coco.getImgIds()
imags = coco.loadImgs(imgIds)

print(imgIds)


annIds = coco.getAnnIds(imgIds=imgIds)
ann = coco.loadAnns(annIds)[0]

mask=coco.annToMask(ann)
rle=coco.annToRLE(ann)

rle=encode(mask)
mask=decode(rle)

area(rle)
toBbox(rle)