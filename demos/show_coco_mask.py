import os

from pycocotools.coco import COCO
from skimage import io
from matplotlib import pyplot as plt

# dataDir=r'G:\datasets\coco\2017'
dataDir = r'C:\work\githome\PyTorch\geojson2coco\data\outcoco'
dataType = 'val2017'
annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
imgDir = os.path.join(dataDir, dataType)

coco = COCO(annFile)

catIds = coco.getCatIds(catNms=['person']) # catIds=1 表示人这一类
imgIds = coco.getImgIds(catIds=catIds ) # 图片id，许多值
for i in range(len(imgIds)):
    img = coco.loadImgs(imgIds[i])[0]
    imgFile = os.path.join(imgDir, img['file_name'])
    I = io.imread(imgFile)
    plt.axis('off')
    plt.imshow(I) #绘制图像，显示交给plt.show()处理
    annIds = coco.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
    anns = coco.loadAnns(annIds)
    coco.showAnns(anns)
    plt.show() #显示图像
