import rasterio
import os

shp_path = '/media/aleko-kon/Daten/Geodaten/Master/GEO419/auxdata/user_shape/dummy_region.shp/'
raster_path = '/media/aleko-kon/Daten/Geodaten/Master/GEO419/auxdata/' \
              'S2A_MSIL2A_20190820T074611_N0213_R135_T35JNH_20190820T120700.SAFE/' \
              'GRANULE/L2A_T35JNH_A021725_20190820T081611/IMG_DATA/R60m/T35JNH_20190820T074611_B04_60m.jp2'

# open raster of most formats via gdal
dataset = rasterio.open(raster_path)

# basic information about the raster
dataset.count
dataset.width
dataset.height
dataset.dtypes
dataset.indexes
dataset.bounds
dataset.transform
dataset.crs

# read band as numpy array
band1 = dataset.read(1)

# indexing: returns the middle pixel
band1[dataset.height // 2, dataset.width // 2]
