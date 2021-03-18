print('geojson2coco convert one')
import os
import json
from osgeo import gdal
import geojson
from shapely.geometry import Polygon



# read image's geo transform through image file
def read_image_geotransform(img_path_file) :

    dataset = gdal.Open(img_path_file, gdal.GA_ReadOnly)

    print("Driver: {}/{}".format(dataset.GetDriver().ShortName,
                                dataset.GetDriver().LongName))
    print("Size is {} x {} x {}".format(dataset.RasterXSize,
                                        dataset.RasterYSize,
                                        dataset.RasterCount))
    print("Projection is {}".format(dataset.GetProjection()))
    geotransform = dataset.GetGeoTransform()
    if geotransform:
        print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
        print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))
    return dataset.RasterXSize, dataset.RasterYSize, geotransform

def read_image_info(img_path_file) :
    dataset = gdal.Open(img_path_file, gdal.GA_ReadOnly)
    image = {'geotransform': dataset.GetGeoTransform(), 'width': dataset.RasterXSize, 'height': dataset.RasterYSize}
    return image


def read_geojson(geojson_path_file) :
    with open(geojson_path_file) as f:
        gj = geojson.load(f)
    features = gj['features']
    segs = []
    for feature in features:
        # feature = features[0]
        ge = feature.geometry

        if ge.type == 'Polygon':
            coos = ge.coordinates
            for coco in coos:
                seg = [i for item in coco for i in item[0:2]]
                segs.append(seg)
        elif ge.type == 'MultiPolygon':
            coos = ge.coordinates
            for coco1 in coos:
                for coco2 in coco1:
                    seg = [i for item in coco2 for i in item[0:2]]
                    segs.append(seg)
        else:
            print("Error: Unknown type in geojson file.")

    return segs

def transform_segs(segs, w, h, trans) :
    x0 = trans[0]
    dx = trans[1]
    y0 = trans[3]
    dy = trans[5]
    segs1 = [(val - x0) / dx if (0 == idx % 2) else (val - y0) / dy for idx, val in enumerate(segs)]
    segs2 = [max(val, 0) for val in segs1]
    segs3 = [min(val, w) if (0 == idx % 2) else min(val, h) for idx, val in enumerate(segs2)]

    return segs3


class Cocowriter:
    def __init__(self):
        self.data = []
        self.imageIndex = 0
        self.annoIndex = 0
        self.images = []
        self.annos = []

        return

    # def AddImage(self, image, image_width, image_height, segs):
    def AddImage(self, image):
        # image data
        image_data = {"file_name": image['pure_image_file'], "height": image['height'], "width": image['width'],
                      "id": self.imageIndex}
        self.images.append(image_data)


        # annoation data
        if len(image['segs']) != 0:
            annotation_data = {"image_id": self.imageIndex, "category_id": 1, "id": self.annoIndex, 'iscrowd': 0,
                               'segmentation': image['segs'], 'bbox': image['bbox'], 'area': image['area']}
            self.annos.append(annotation_data)
            self.annoIndex = self.annoIndex + 1


        self.imageIndex = self.imageIndex + 1

        return

    def FillImages(self, data):
        # fill image data
        # image_data = {"file_name": "3band_AOI_1_RIO_img135.tif", "height": 512, "width": 512, "id": 0}
        # image_data['file_name'] = img_file
        for image in self.images:
            data['images'].append(image)

    def FillAnnotation(self, data):
        for anno in self.annos:
            data['annotations'].append(anno)

    def FillCategory(self, data):
        # category_data = {"supercategory": "person", "id": 0, "name": "person"}
        data['categories'].append({"supercategory": "outlier", "id": 0, "name": "outlier"})
        data['categories'].append({"supercategory": "horse", "id": 1, "name": "horse"})

    def Save(self):
        data = {
            "info": {},
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": []
        }

        # fill image data
        self.FillImages(data)

        # fill annotation data
        self.FillAnnotation(data)

        # fill categories data
        self.FillCategory(data)

        # write files
        with open(output_file, "w") as write_file:
            json.dump(data, write_file)


import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import box
from shapely.ops import unary_union


def seg_to_bbox(seg):
    npseg = np.array(seg)
    npseg1 = npseg.reshape(npseg.shape[0] // 2, 2)
    po = Polygon(npseg1)
    b = box(*po.bounds)
    return b


def segs_to_bbox(segs):
    boxes = [seg_to_bbox(s) for s in segs]
    u = unary_union(boxes)
    return u.bounds

def seg_to_poly(seg):
    npseg = np.array(seg)
    npseg1 = npseg.reshape(npseg.shape[0] // 2, 2)
    po = Polygon(npseg1)
    return po

def segs_to_area(segs):
    polys = [seg_to_poly(s) for s in segs]
    u = unary_union(polys)
    return u.area

def convert_one_image(writer, image_pathname, geojson_pathname):
    # image_width, image_height, img_geotransform = read_image_geotransform(image_pathname)

    image = read_image_info(image_pathname)
    segs0 = read_geojson(geojson_pathname)
    segs1 = [transform_segs(seg, image['width'], image['height'], image['geotransform']) for seg in segs0]

    image['area'] = segs_to_area(segs1)
    image['bbox'] = list(segs_to_bbox(segs1))
    image['pure_image_file'] = os.path.basename(image_pathname)
    # image = {}
    # image['pure_image_file'] = pure_image_file
    # image['width'] = image_width
    # image['height'] = image_height
    image['segs'] = segs1
    # writer.AddImage(pure_image_file, image_width, image_height, segs1)
    writer.AddImage(image)


import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='C:/work/githome/PyTorch/geojson2coco/data/3band/', help='')
    parser.add_argument('--geojson', type=str, default='C:/work/githome/PyTorch/geojson2coco/data/geojson/', help='')
    parser.add_argument('--output-file', type=str, default='../data/outcoco/annotations/instances_val2017.json', help='')

    opt = parser.parse_args()

    if os.path.isdir(opt.image) and os.path.isdir(opt.geojson):
        for img_path, _, images in os.walk(opt.image):
            img_path_names = [os.path.join(img_path, i) for i in images]
            break
        for geojson_path, _, geojsons in os.walk(opt.geojson):
            geojson_path_names = [os.path.join(geojson_path, i) for i in geojsons]
            break

    elif os.path.isfile(opt.image) and os.path.isfile(opt.geojson) :
        img_path_names = [opt.image]
        geojson_path_names = [opt.geojson]

    else:
        print('parameter error')
        exit(1)






    # define path and filename
    # data_dir = 'C:/work/githome/PyTorch/geojson2coco/data'
    # image_dir = os.path.join(data_dir, '3band').replace('\\', '/')
    # geojson_dir = os.path.join(data_dir, 'geojson').replace('\\', '/')
    #


    # img_file = '3band_AOI_1_RIO_img135.tif'
    # geojson_file = 'Geo_AOI_1_RIO_img135.geojson'
    # img_file = '3band_AOI_1_RIO_img100.tif'
    # geojson_file = 'Geo_AOI_1_RIO_img100.geojson'
    # output_file = '../data/outcoco/annotations/instances_val2017.json'
    output_file = opt.output_file
    # img_path_file = os.path.join(image_dir, img_file).replace('\\', '/')
    # geojson_path_file = os.path.join(geojson_dir, geojson_file).replace('\\', '/')

    img_geojson_list = zip(img_path_names, geojson_path_names)



    writer = Cocowriter()


    # convert_one_image(writer, img_path_file, geojson_path_file)
    i = 0
    for img_pathname, geojson_pathname in img_geojson_list:
        convert_one_image(writer, img_pathname, geojson_pathname)
        # i = i+1
        # if i==90:
        #     break

    writer.Save()


