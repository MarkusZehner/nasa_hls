import rasterio
import os
from spatialist import Vector
import rasterio
import glob
from osgeo import gdal

# make user directory
# download kml file in this directory
path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata')
os.mkdir(path + '/')

# here the user shapes should be placed
path_data = '/home/aleko-kon/.nasa_hls/data/'
os.mkdir(path_data)


path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata')

# get directory of hdfs
# load hdfs in vrt
# load shape in vrt
# make mosaic of hdfs
# crop mosaic with shape
# export to directory of hdfs

vrt = os.path.join(path, 'auxdata', 'test.vrt')


shp_path = '/home/robin/python_projects/data/nasa_hls/test_shape/dummy_region.shp'

with Vector(shp_path) as site:
    dem_autoload([site], 'SRTM 1Sec HGT', vrt=vrt)

options = gdal.WarpOptions(format='GTiff')

gdal.Warp(destNameOrDestDS='test.tif', srcDSOrSrcDSTab='test.vrt', options=options)


### try it with rasterio

hdf_path = "/home/robin/python_projects/data/nasa_hls/hdf_tiles"

for i in glob(os.path.join(hdf_path, "/*.hdf"))
    with rasterio.open(i) as src: 

shadow = gdal.BuildVRT('/home/robin/python_projects/data/vrt', my_hdfs)


### try it with python-gdal
vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True, bandList=[])
my_hdfs = list(glob.glob(os.path.join("/home/robin/python_projects/data/nasa_hls/hdf_tiles",'*.hdf')))

# make list with gdal datasets
gdal_datasets = []
for i in my_hdfs:
    dataset = gdal.Open(i)
    gdal_datasets.append(dataset)

# loop over list and create vrts
vrts = []
for i in my_hdfs:
    vrt = gdal.BuildVRT(os.path.join(i, ".vrt"), i, options=vrt_options)
    vrts.append(vrt)

# convert vrt to tiff
gdal.Translate(".tif",vrts[1])
    



