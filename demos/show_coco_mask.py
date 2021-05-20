import os

from pycocotools.coco import COCO
from skimage import io
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import cv2
import numpy as np


# dataDir=r'G:\datasets\coco\2017'
dataDir = r'C:\work\githome\PyTorch\geojson2coco\data\outcoco'
dataDir = r'E:\work\githome\PyTorch\mmdetection\mydemos\TestDataFromGEOJSON_Simple\data'
dataDir = r'G:\datasets\coco\2017'
dataType = 'val2017'
annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
imgDir = os.path.join(dataDir, dataType)

coco = COCO(annFile)

catIds = coco.getCatIds('horse')
imgIds = coco.getImgIds(catIds=catIds)
annIds = coco.getAnnIds(imgIds=imgIds)

imgs = coco.loadImgs(imgIds)

for img in imgs:
    imgFile = os.path.join(imgDir, img['file_name'])
    image = cv2.imread(imgFile)

    annIds = coco.getAnnIds(imgIds=[img['id']], catIds=catIds)
    anns = coco.loadAnns(annIds)

    for ann in anns:
        # Draw bbox
        x, y, w, h = ann['bbox']
        image = cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 255), 2)

        # Draw segmentation
        segs = ann["segmentation"]
        segs = [np.array(seg, np.int32).reshape((1, -1, 2))
                for seg in segs]
        for seg in segs: cv2.drawContours(image, seg, -1, (0, 255, 0), 2)

        mask = coco.annToMask(ann)
        mask1 = np.transpose(mask)
        mask2 = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        image = image + mask2*128
        mask3 = mask2*255
        image = cv2.addWeighted(image, 1, mask3, 0.3, 0.0)
        shape = mask1.shape
        shape1 = image.shape

    cv2.imshow('demo', image)
    cv2.waitKey(5000)

