import rasterio
import os
from spatialist import Vector
import rasterio
import glob
from osgeo import gdal
import os.path
import sys


def main():

    
    # make user directory
    # download kml file in this directory
    path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata')
    # check for kml download path
    if not os.path.exists(path):
        os.mkdir(path + '/')
    else:
        pass

    

    # here the user shapes should be placed
    path_data = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.data')
    if not os.path.exists(path_data):
        os.mkdir(path_data + "/")
    else:
        pass




        for i in nrow(datasets):
            dstdir = dstdir + i
            download_batch(dstdir)



    # get directory of hdfs
    # load hdfs in vrt
    # load shape in vrt
    # make mosaic of hdfs
    # crop mosaic with shape
    # export to directory of hdfs

    # get the user directory for the hdf path
    print("plese specidfy the directory for the hdfs")
    hdf_dir = str(input())
    

    # make list with all the .hdf files in the directory
    hdf_dir = "/home/robin/python_projects/data/nasa_hls/hdf_tiles/"
    # "/home/robin/python_projects/data/nasa_hls/hdf_tiles"
    hdf_path = list(glob.glob(os.path.join(hdf_dir, '*.hdf')))

    # make list with gdal datasets
    # gdal_datasets = []
    # for i in hdf_path:
    #     dataset = gdal.Open(i)
    #     gdal_datasets.append(dataset)

    # build vrt with all from all the -hdf files specified
    # print("making vrt")
    # vrt_path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.data', "hls.vrt")
    # vrt = gdal.BuildVRT(vrt_path, gdal_datasets)

    # shape path
    # shp_path = '/home/robin/python_projects/data/nasa_hls/test_shape/dummy_region.shp'

    ###############
    ####### Mak VRT
    ################

    # set vrt-options. Don't know why, but on the command line requires different projections
    vrtoptions = gdal.BuildVRTOptions(allowProjectionDifference=True, separate=True)
    vrt_path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.data', "final_py.vrt")
    print("the path where your vrt and final tiff will be is: \n {path}".format(path = vrt_path))

    # make vrt 
    final_vrt = gdal.BuildVRT(vrt_path, hdf_path, options=vrtoptions)

    #get projection
    projection = final_vrt.GetProjection()

    # reproject vrt
    final_vrt = gdal.Warp(vrt_path, final_vrt, dstSRS=projection)
    final_vrt = None

    # convert vrt to tiff
    final_tif = gdal.Translate(os.path.join(path_data + "/" + "final2.tiff"), vrt_path, projWinSRS=projection)
    print("\nfinal tif created \n")
    print("Now proceed to clipping \n")

    # use Johns spatialist to clip
    # from pyroSAR.auxdata import dem_autoload
    # with Vector(shp_path) as site:
    #     dem_autoload([site], 'SRTM 1Sec HGT', vrt=vrt)
    # result.tif
    #with Vector(shp_path) as site:
    #    with Raster('result.tif')[site] as ras:
    #        mat = ras.array()

    return None

if __name__ == "__main__":
    main()




