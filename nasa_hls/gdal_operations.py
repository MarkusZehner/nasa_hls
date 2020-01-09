import rasterio
import os
from spatialist import Vector
import rasterio

# make user directory
# download kml file in this directory
path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata')
os.mkdir(path + '/')

# here the user shapes should be placed
path_data = '/home/aleko-kon/.nasa_hls/data/'
os.mkdir(path_data)


vrt = os.path.join(path, 'auxdata', 'test.vrt')


shp_path = '/home/robin/python_projects/data/nasa_hls/test_shape/dummy_region.shp'

with Vector(shp_path) as site:
    dem_autoload([site], 'SRTM 1Sec HGT', vrt=vrt)

options = gdal.WarpOptions(format='GTiff')

gdal.Warp(destNameOrDestDS='test.tif', srcDSOrSrcDSTab='test.vrt', options=options)Vect