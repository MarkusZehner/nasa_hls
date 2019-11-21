import rasterio
import os
from spatialist import Vector


#auxpath
path = os.path.join(os.path.expanduser('~'), '.nasa_hls')

path = '/media/aleko-kon/Daten/Geodaten/Master/GEO419'

vrt = os.path.join(path, 'auxdata', 'test.vrt')


shp_path = '/media/aleko-kon/Daten/Geodaten/Master/GEO419/auxdata/user_shape/dummy_region.shp/'

with Vector(shp_path) as site:
    dem_autoload([site], 'SRTM 1Sec HGT', vrt=vrt)

options = gdal.WarpOptions(format='GTiff')

gdal.Warp(destNameOrDestDS='test.tif', srcDSOrSrcDSTab='test.vrt', options=options)Vect