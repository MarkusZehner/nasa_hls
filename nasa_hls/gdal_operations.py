import rasterio
import os
from spatialist import Vector


# make user directory
# download kml file in this directory
path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata2') + '/'
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


shp_path = '/media/aleko-kon/Daten/Geodaten/Master/GEO419/auxdata/user_shape/dummy_region.shp/'

with Vector(shp_path) as site:
    dem_autoload([site], 'SRTM 1Sec HGT', vrt=vrt)

options = gdal.WarpOptions(format='GTiff')

gdal.Warp(destNameOrDestDS='test.tif', srcDSOrSrcDSTab='test.vrt', options=options)Vect