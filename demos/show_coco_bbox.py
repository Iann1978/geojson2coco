import json
import os
import cv2
from pycocotools.coco import COCO

#dataDir=r'G:\datasets\coco\2017'
dataDir = r'E:\work\githome\PyTorch\mmdetection\mydemos\TestDataFromGEOJSON_Simple\data'
dataType = 'val2017'
imgDir = os.path.join(dataDir, dataType)
annFile = '{}/annotations/instances_{}.json'.format(dataDir,dataType)

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
        x, y, w, h = ann['bbox']
        # 参数为(图像，左上角坐标，右下角坐标，边框线条颜色，线条宽度)
        # 注意这里坐标必须为整数，还有一点要注意的是opencv读出的图片通道为BGR，所以选择颜色的时候也要注意
        image = cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 255), 2)

    cv2.imshow('demo', image)
    cv2.waitKey(5000)
