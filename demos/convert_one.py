print('geojson2coco convert one')
import os
from osgeo import gdal

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

img_geotransform = read_image_geotransform(img_path_file)

print(img_geotransform)


import json

data = {
    "info": {},
    "licenses": [],
    "images": [],
    "annotations": [],
    "categories": []
}

# fill image data
image_data = {"file_name": "3band_AOI_1_RIO_img135.tif", "height": 512, "width": 512, "id": 0}
image_data['file_name'] = img_file
data['images'].append(image_data)

# fill annotation data
annotation_data0 = {
    "image_id": 289343,
    "id": 433580,
    "caption": "A person riding a very tall bike in the street."
}
annotation_data1 = {
    "segmentation": [[10.0, 10.0, 100.0, 100.0, 10.0, 100.0, 10.0, 10.0]],
    "area": 260334.25,
    "iscrowd": 0,
    "image_id": 0,
    "bbox": [-0.5, -0.5, 512.0, 512.0],
    "category_id": 0,
    "id": 0
}

# data['annotations'].append(annotation_data0)
data['annotations'].append(annotation_data1)

# fill categories data
category_data = {"supercategory": "person", "id": 0, "name": "person"}
data['categories'].append(category_data)

# fill segmentation data

# [{"supercategory": "outlier", "id": 0, "name": "outlier"}, {"supercategory": "horse", "id": 1, "name": "horse"}]

with open(output_file, "w") as write_file:
    json.dump(data, write_file)



# read geojson
import geojson
with open(geojson_path_file) as f:
    gj = geojson.load(f)
features = gj['features']
feature = features[0]
ge = feature.geometry
coo = ge.coordinates
coo0 = coo[0]
seg = [i for item in coo0 for i in item[0:2]]


coordinates = feature.coordinates
segmentation_data = [x for x in coordinates[0]]

feature_number = len(features)



a = 0


feature0 = features[0]

b = 0
# import geojson
# data = geojson.loads(geojson_path_file)
# print(data)