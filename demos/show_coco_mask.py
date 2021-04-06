import os

from pycocotools.coco import COCO
from skimage import io
from matplotlib import pyplot as plt
import matplotlib.patches as patches

# dataDir=r'G:\datasets\coco\2017'
dataDir = r'C:\work\githome\PyTorch\geojson2coco\data\outcoco'
dataDir = r'E:\work\githome\PyTorch\mmdetection\mydemos\TestDataFromGEOJSON_Simple\data'
# dataDir = r'G:\datasets\coco\2017'
dataType = 'val2017'
annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
imgDir = os.path.join(dataDir, dataType)

coco = COCO(annFile)

catIds = coco.getCatIds(catNms=['horse']) # catIds=1 表示人这一类
#catIds = coco.getCatIds(catNms=['person']) # catIds=1 表示人这一类
imgIds = coco.getImgIds(catIds=catIds ) # 图片id，许多值
imageCount = len(imgIds)

for i in range(len(imgIds)):
    fig, ax = plt.subplots()

    img = coco.loadImgs(imgIds[i])[0]
    imgFile = os.path.join(imgDir, img['file_name'])
    I = io.imread(imgFile)
    ax.axis('off')
    ax.imshow(I) #绘制图像，显示交给plt.show()处理
    annIds = coco.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
    anns = coco.loadAnns(annIds)
    # bbox = anns[0]['bbox']

    coco.showAnns(anns)
    for ann in anns:
        bbox = ann['bbox']
        rect = patches.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                                 linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
    plt.show() #显示图像
