import rasterio
import os
from spatialist import Vector
import rasterio
import glob
from osgeo import gdal
import os.path
import sys
from nasa_hls.utils import BAND_NAMES
sys.path.append("/home/robin/python_projects/nasa_hls")
from nasa_hls.download_tiles import get_available_datasets_from_shape
from nasa_hls.download_hls_dataset import download_batch
from nasa_hls.download_tiles import path_data_lin_robin
from nasa_hls.download_tiles import path_data_lin_konsti

gdal.UseExceptions()

# make mosaic function
def make_mosaic_tif(srcdir = path_data_lin_robin + "hdf/", dstdir = path_data_lin_robin + "mosaic/", bands = None, product = None):

    """
    :param bands --> list with band names e.g ["bando1", "band02", ...] see utily.py for all bands
                     if None, all bands will be used
            
    """

    # get all hdf-files
    hdf_files_list = list(glob.glob(srcdir + '*.hdf'))

    # make list of all dates in directory
    dates_doy = []
    for line in hdf_files_list:
        l = line.split(".")[3][4:]
        dates_doy.append(l)

    # print list with unique dates
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

    # for each datum (key) print absolute paths (values)
    # for key, item in dataframe_dict.items():
         #print(key, item, "\n")

    #check if band is specified
    if bands is None:
        bands = list(BAND_NAMES[product].keys())
        long_band_names = []
        for long_band_name in bands:
            band = BAND_NAMES[product][long_band_name]
            long_band_names.append(band)
   
    # make dictionary with all bands for date as values
    dates_dict = {date: None for date in unique_doy}

    for key in dataframe_dict.keys():
    #     # print(key)
    #     # hdf_list ist eine Liste mit allen Datensätzen für das Datum

    #     ##########    
    #     # For Date 
    #     # ########   
        hdf_list = dataframe_dict[key]

    #     # list of vrts for each band
    #     date_vrt = []

    #     ##########
    #     # For Band
    #     ##########
    #     for band in long_band_names:
    #         # make a list for each band at that date with the format: HDF4_EOS:EOS_GRID:"{...hdf}":Grid:{band}'
    #         single_band_date_2o4_tiles = []
            
             
    #     ##########
    #     # For HDF
    #     ##########   
    #         for single_hdf in hdf_list:            
    #             # make filnename for all scenes with that date, specifying the band
    #             hdf_single_band = 'HDF4_EOS:EOS_GRID:"{0}":Grid:{1}'.format(single_hdf, band)
    #             # append this file to the list for each band and date
    #             single_band_date_2o4_tiles.append(hdf_single_band)

        
    #         vrt_band_date_mosaic = os.path.join(path_data_lin_robin + "mosaic" + band + ".vrt")
    #         #build vrt for each band for each date
    #         build_vrt = gdal.BuildVRT(vrt_band_date_mosaic, single_band_date_2o4_tiles)
    #         date_vrt.append(build_vrt)
    #         #build_vrt = None


    #     # Build VRTs for each date (in the hdf_list-loop)
    #     final_vrt_path = os.path.join(path_data_lin_robin + key + ".vrt")
    #     vrt_date_mosaic = gdal.BuildVRT(final_vrt_path, date_vrt)
    #     final_tif = gdal.Translate(os.path.join(path_data_lin_robin + "mosaic/" + key + ".tiff"), vrt_date_mosaic)
    #     vrt_date_mosaic = None
    #     final_tif = None

    ###########
    # Alternative
    ###########

        for key in dates_dict.keys():
            all_bands = []
            for single_file in hdf_list:    
                for band in long_band_names:
                    single_file_single_band = 'HDF4_EOS:EOS_GRID:"{0}":Grid:{1}'.format(single_file, band)
                    all_bands.append(single_file_single_band)

            dataframe_dict[key] = all_bands
                    
        print(dates_dict)



    # return None
