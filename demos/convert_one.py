print('geojson2coco convert one')
import os
import json
from osgeo import gdal
import geojson

# define path and filename
data_dir = 'C:/work/githome/PyTorch/geojson2coco/data'
image_dir = os.path.join(data_dir, '3band').replace('\\', '/')
geojson_dir = os.path.join(data_dir, 'geojson').replace('\\', '/')
img_file = '3band_AOI_1_RIO_img135.tif'
geojson_file = 'Geo_AOI_1_RIO_img135.geojson'
output_file = '../data/outcoco/annotations/instances_val2017.json'
img_path_file = os.path.join(image_dir, img_file).replace('\\', '/')
geojson_path_file = os.path.join(geojson_dir, geojson_file).replace('\\', '/')

print(img_path_file)
print(geojson_path_file)

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
    return geotransform

def read_geojson(geojson_path_file) :
    with open(geojson_path_file) as f:
        gj = geojson.load(f)
    features = gj['features']
    feature = features[0]
    ge = feature.geometry
    coo = ge.coordinates
    coo0 = coo[0]
    seg = [i for item in coo0 for i in item[0:2]]
    return seg

def transform_segs(segs, trans) :
    x0 = trans[0]
    dx = trans[1]
    y0 = trans[3]
    dy = trans[5]
    new_segs = [(val - x0) / dx if (0 == idx % 2) else (val - y0) / dy for idx, val in enumerate(segs)]
    return new_segs


class Cocowriter:
    def __init__(self):
        self.data = []
        self.imageIndex = 0
        self.annoIndex = 0

        return

    def AddImage(self, image, segs):

        # image data
        image_data = {"file_name": "", "height": 512, "width": 512, "id": self.imageIndex}
        image_data["file_name"] = image


        # annoation data
        annotation_data = {
            "segmentation": [],
            "area": 260334.25,
            "iscrowd": 0,
            "image_id": self.imageIndex,
            "bbox": [-0.5, -0.5, 512.0, 512.0],
            "category_id": 0,
            "id": self.annoIndex
        }
        annotation_data['segmentation'].append(segs)


        self.imageIndex = self.imageIndex + 1
        self.annoIndex = self.annoIndex + 1

        self.images = image_data
        self.annos = annotation_data
        return

    def FillImages(self, data):
        # fill image data
        # image_data = {"file_name": "3band_AOI_1_RIO_img135.tif", "height": 512, "width": 512, "id": 0}
        # image_data['file_name'] = img_file
        data['images'].append(self.images)

    def FillAnnotation(self, data):
        data['annotations'].append(self.annos)

    def FillCategory(self, data):
        category_data = {"supercategory": "person", "id": 0, "name": "person"}
        data['categories'].append(category_data)

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


img_geotransform = read_image_geotransform(img_path_file)
seg0 = read_geojson(geojson_path_file)
seg1 = transform_segs(seg0, img_geotransform)
writer = Cocowriter()
writer.AddImage(img_file, seg1)
writer.Save()






