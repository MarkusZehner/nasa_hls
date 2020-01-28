import rasterio
import os
from spatialist import Vector
import rasterio
import glob
from osgeo import gdal
import os.path
import sys
sys.path.append("/home/robin/python_projects/nasa_hls")
from nasa_hls.download_tiles import get_available_datasets_from_shape
from nasa_hls.download_hls_dataset import download_batch
from nasa_hls.download_tiles import path_data_lin_robin
from nasa_hls.download_tiles import path_data_lin_konsti

# make mosaic function
def make_mosaic_tif(srcdir = path_data_lin_robin +"hdf/", dstdir = path_data_lin_robin + "mosaic/"):
