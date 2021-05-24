print('spacenet_to_coco')

import os
import cv2
import numpy as np
from osgeo import gdal
import json
import geojson
from shapely.geometry import Polygon
from shapely.geometry import box
from shapely.ops import unary_union

class ConvertImage:
    def __init__(self):
        return
    def LoadTiff(self, tif_pathfile):
        self.tif_pathfile = tif_pathfile
        dataset = gdal.Open(tif_pathfile, gdal.GA_ReadOnly)
        geotransform = dataset.GetGeoTransform()

        self.geotransform = {"x":geotransform[0], "y": geotransform[3],
                             "dx":geotransform[1], "dy":geotransform[5],
                             'width': dataset.RasterXSize, 'height': dataset.RasterYSize}

        print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
        print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))

    def LoadGeoJson(self, geojson_pathfile):
        geosegs = self.ReadGeoSegs(geojson_pathfile)
        self.segs = self.ConvertGeoSegsToCocoSegs(geosegs)
        return


    def ReadGeoSegs(self, geojson_path_file):
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

    def ConvertOneGeoSegToCocoSeg(self, segs):
        w = self.geotransform["width"]
        h = self.geotransform["height"]
        x0 = self.geotransform["x"]
        y0 = self.geotransform["y"]
        dx = self.geotransform["dx"]
        dy = self.geotransform["dy"]
        # x0 = trans[0]
        # dx = trans[1]
        # y0 = trans[3]
        # dy = trans[5]
        segs1 = [(val - x0) / dx if (0 == idx % 2) else (val - y0) / dy for idx, val in enumerate(segs)]
        segs2 = [max(val, 0) for val in segs1]
        segs3 = [min(val, w) if (0 == idx % 2) else min(val, h) for idx, val in enumerate(segs2)]

        return segs3

    def ConvertGeoSegsToCocoSegs(self, segs0):
        segs1 = [self.ConvertOneGeoSegToCocoSeg(seg) for seg in segs0]
        return segs1

    def SavePng(self, png_pathfile):
        self.png_pathfile = png_pathfile
        img = cv2.imread(self.tif_pathfile, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)
        img2 = img.astype(np.float32)
        img3 = img2 / 1024 * 255
        img4 = np.clip(img3, 0, 255)
        img5 = img4.astype(np.uint8)
        cv2.imwrite(self.png_pathfile, img5)
        return


class CocoAnnWriter:
    def __init__(self):
        self.data = []
        self.imageIndex = 0
        self.annoIndex = 0
        self.images = []
        self.annos = []

        return

    def seg_to_bbox(self, seg):
        npseg = np.array(seg)
        npseg1 = npseg.reshape(npseg.shape[0] // 2, 2)
        po = Polygon(npseg1)
        b = box(*po.bounds)
        return b

    def segs_to_bbox(self,segs):
        boxes = [self.seg_to_bbox(s) for s in segs]
        u = unary_union(boxes)
        return u.bounds

    def seg_to_poly(self, seg):
        npseg = np.array(seg)
        npseg1 = npseg.reshape(npseg.shape[0] // 2, 2)
        po = Polygon(npseg1)
        return po

    def segs_to_area(self, segs):
        polys = [self. seg_to_poly(s) for s in segs]
        u = unary_union(polys)
        return u.area

    # def AddImage(self, image, image_width, image_height, segs):
    def AddImage(self, image):
        # image data
        _, image_name = os.path.split(image.png_pathfile)
        image_data = {"file_name": image_name,
                      "width": image.geotransform['width'],
                      "height": image.geotransform['height'],
                      "id": self.imageIndex}
        self.images.append(image_data)

        # annoation data
        if len(image.segs) != 0:
            for seg in image.segs:
                area = self.segs_to_area([seg])
                bbox = list(self.segs_to_bbox([seg]))
                bbox[2] = bbox[2] - bbox[0]
                bbox[3] = bbox[3] - bbox[1]

                annotation_data = {"id": self.annoIndex,
                                   "image_id": self.imageIndex,
                                   "category_id": 0,
                                   'iscrowd': 0,
                                   'segmentation': [seg],
                                   'bbox': bbox,
                                   'area': area}

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
        data['categories'].append({"supercategory": "house", "id": 0, "name": "house"})


    def Save(self, output_file):
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

if __name__ == '__main__':

    spacenet_path = 'data/spacenet'
    coco_path = 'data/coco'

    tif_path = os.path.join(spacenet_path, 'PS-RGB')
    png_path = os.path.join(coco_path, "val2017")
    geojson_path = os.path.join(spacenet_path,'geojson_buildings')

    for _, _, filenames in os.walk(tif_path):
        tif_filenames = filenames

    for _, _, filenames in os.walk(geojson_path):
        geojson_filenames = filenames


    tif_geojson_pathfiles = zip(tif_filenames, geojson_filenames)


    annWriter = CocoAnnWriter()

    for tif_filename, geojson_filename in tif_geojson_pathfiles:
        png_filename = os.path.splitext(tif_filename)[0]+'.png'
        print("\n")
        # print("tif_filename:", tif_filename)
        # print("png_filename:", png_filename)
        # print("geojson_filename:", geojson_filename)
        tif_pathfile = os.path.join(tif_path, tif_filename)
        png_pathfile = os.path.join(png_path, png_filename)
        geojson_pathfile = os.path.join(geojson_path, geojson_filename)
        tif_pathfile = tif_pathfile.replace('\\','/')
        png_pathfile = png_pathfile.replace('\\','/')
        geojson_pathfile = geojson_pathfile.replace('\\','/')
        print("tif_pathfile:", tif_pathfile)
        print("png_pathfile:", png_pathfile)
        print("geojson_pathfile:", geojson_pathfile)




        tif_pathfile1 = 'data/spacenet/PS-RGB/SN2_buildings_train_AOI_4_Shanghai_PS-RGB_img11.tif'
        png_pathfile1 = 'data/coco/val2017/SN2_buildings_train_AOI_4_Shanghai_PS-RGB_img11.png'
        geojson_pathfile1 = 'data/spacenet/geojson_buildings/SN2_buildings_train_AOI_4_Shanghai_geojson_buildings_img11.geojson'

        convertImage = ConvertImage()
        convertImage.LoadTiff(tif_pathfile)
        convertImage.LoadGeoJson(geojson_pathfile)
        convertImage.SavePng(png_pathfile)
        annWriter.AddImage(convertImage)

    ann_pathfile = 'data/coco/annotations/instances_val2017.json'
    annWriter.Save(ann_pathfile)

    # tif_pathfile = 'data/spacenet/PS-RGB/SN2_buildings_train_AOI_4_Shanghai_PS-RGB_img3.tif'
    # png_pathfile = 'data/coco/val2017/SN2_buildings_train_AOI_4_Shanghai_PS-RGB_img3.png'
    # geojson_pathfile = 'data/spacenet/geojson_buildings/SN2_buildings_train_AOI_4_Shanghai_geojson_buildings_img3.geojson'
    # ann_pathfile = 'data/coco/annotations/instances_val2017.json'
    #
    #
    # annWriter = CocoAnnWriter()
    # convertImage = ConvertImage()
    # convertImage.LoadTiff(tif_pathfile)
    # convertImage.LoadGeoJson(geojson_pathfile)
    # convertImage.SavePng(png_pathfile)
    #
    # annWriter.AddImage(convertImage)
    # annWriter.Save(ann_pathfile)


