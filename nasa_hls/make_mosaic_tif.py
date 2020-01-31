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

gdal.UseExceptions()

# make mosaic function
def make_mosaic_tif(srcdir = path_data_lin_robin + "hdf/", dstdir = path_data_lin_robin + "mosaic/"):

    # get all hdf-files
    hdf_files_list = list(glob.glob(srcdir + '*.hdf'))

    # make list of all dates in directory
    dates_doy = []
    for line in hdf_files_list:
        l = line.split(".")[3][4:]
        dates_doy.append(l)

    # print list with unique
    #print(dates_doy)

    # make a function that gets the unique entries from a list
    # these will be the keys afterwards
    def unique_dates(liste):
        unique_dates = []
        for x in liste:
            if x not in unique_dates:
                unique_dates.append(x)
        return unique_dates
    
    # make the list of unique dates
    unique_doy = unique_dates(dates_doy)

    # create dictionary with keys being the unique dates
    # not yet specify the value-type
    dataframe_dict = {date: None for date in unique_doy}

    # add rows of orignial dataframe as values
    for key in dataframe_dict.keys():
        foo = []
        # now go over all the files
        for line in hdf_files_list:
            # get the doy
            line_date = line.split(".")[3][4:]
            # wenn doy in der line == dem key, dann schreib es in die liste foo
            if key == line_date:
                foo.append(line)
        # nachdem du über alle files gegangen bist, schreib an den key mit dem doy die aktuelle foo-liste,
        # die nach diesem Durchgang wieder neu aufgesetzt wird
        dataframe_dict[key] = foo


    for key, item in dataframe_dict.items():
         print(key, item, "\n")

    

    for key in dataframe_dict.keys():
        print(key)
        hdf_list = dataframe_dict[key]
        band = 'B02'
        hdf_list = ['HDF4_EOS:EOS_GRID:"{0}":Grid:{1}'.format(x, band) for x in hdf_list]
        print('\n'.join(hdf_list))
        vrt_path = os.path.join(path_data_lin_robin, "mosaic", "mosaic" + key + ".vrt")
        build_vrt = gdal.BuildVRT(vrt_path, hdf_list)
        if build_vrt is None:
            continue
        build_vrt.FlushCache()
        # build_vrt = None
        final_tif = gdal.Translate(os.path.join(path_data_lin_robin + "mosaic/" + key + ".tiff"), build_vrt)
        final_tif = None
        build_vrt = None


    # # vrt_path = os.path.join(path_data_lin_robin, "mosaic", "mosaic.vrt")
    # # # make vrt 
    # # final_vrt = gdal.BuildVRT(vrt_path, hdf_files_list)
    # # final_vrt = None

    # # # make tif
    # # final_tif = gdal.Translate(os.path.join(path_data_lin_robin + "mosaic/" + "final.tiff"), vrt_path)

    # return None
