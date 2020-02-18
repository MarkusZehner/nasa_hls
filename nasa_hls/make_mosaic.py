import os
import glob
from osgeo import gdal

from .download_tiles import path_auxil
from .utils import BAND_NAMES

gdal.UseExceptions()


def make_mosaic(srcdir=None, dstdir=None, bands=None, product="S30"):

    options = gdal.BuildVRTOptions(separate=True)
    
    # get all hdf-files
    hdf_files_list = list(glob.glob(srcdir + '*.hdf'))
    #print(hdf_files_list)

    # make list of all dates in directory
    dates_doy = []
    for line in hdf_files_list:
        l = line.split(".")[3][4:]
        dates_doy.append(l)

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

    # print(dataframe_dict["311"], "\n\n")
    # for key, item in dataframe_dict.items():
    # print(key, item, "\n")

    # check if band is specified
    if bands is None:
        bands = list(BAND_NAMES[product].keys())
        long_band_names = []
        for long_band_name in bands:
            band = BAND_NAMES[product][long_band_name]
            long_band_names.append(band)
    else:
        long_band_names = bands

    if not os.path.exists(path_auxil + "mosaic/bands/"):
        os.makedirs(os.path.join(path_auxil + "mosaic/bands/"))

    for key in dataframe_dict.keys():
        for band in long_band_names:
            hdf_list = dataframe_dict[key]
            hdf_file_bands = []
            for hdf_file in hdf_list:
                filename = 'HDF4_EOS:EOS_GRID:"{0}":Grid:{1}'.format(hdf_file, band)
                hdf_file_bands.append(filename)

            # print("\n".join(hdf_file_bands))
            # make mosaics for each band for each date
            vrt_path = os.path.join(path_auxil + "mosaic/bands/" + key + band + ".vrt")
            build_vrt = gdal.BuildVRT(vrt_path, hdf_file_bands, options = options)
            build_vrt = None
    
    #depricated??!
    #dates_dict = {date: None for date in unique_doy}

    # list of vrts
    print("the unique days are: \n", unique_doy, "\n")
    print("now all the vrts\n")
    vrts = list(glob.glob(path_auxil + "mosaic/bands/" + "*.vrt"))
    print(vrts)

    # make list of bands
    days = []
    for i in unique_doy:
        days_unique = []
        for j in vrts:
            if j.split(".")[2][-9:-6] == i:
                days_unique.append(j)
            
        days.append(days_unique)

    print("this is days[0]", "\n", days[0])
    # get band in every string for sorting
    def getBand(foo):
        """
        param: foo (string)
        """
        return foo.split(".")[2][-2:]

    for i in days:
        i.sort(key = getBand)

    
    #make final vrts and tifs
    if not os.path.exists(path_auxil + "mosaic/days/"):
        os.makedirs(os.path.join(path_auxil + "mosaic/days/"))
    vrt_days = os.path.join(path_auxil + "mosaic/days/")

    for i in days:
        #print("\n\n\n", "this is i" , "\n", i)
        vrt_path = os.path.join(vrt_days + i[0][-13:-10] + "final.vrt")
        #print(vrt_path)
        single_vrt = gdal.BuildVRT(vrt_path, i, options = options)
        tiff_path = os.path.join(dstdir + i[0][-13:-10] + ".tiff")
        tif = gdal.Translate(tiff_path, single_vrt)


    # # print(vrts)
    # for key in dates_dict.keys():
    #     files = []
    #     for single_file in vrts:
    #         doy = single_file.split("/")[-1][0:3]
    #         if key == doy:
    #             files.append(single_file)

    #     dates_dict[key] = files

    # ######is
    # # print the dict
    # #####
    # # for keys, items in dates_dict.items():
    # #    print(keys, items, "\n")
    # # print dictionary nicely
    # # print("\n".join("{}\t{}".format(k, v) for k, v in dates_dict.items()))
    # # print(len(dates_dict))

    # if not os.path.exists(path_auxil + "mosaic/days/"):
    #     os.makedirs(os.path.join(path_auxil + "mosaic/days/"))
    # vrt_days = os.path.join(path_auxil + "mosaic/days/")

    # for date in dates_dict.keys():
    #     print(date)

    #     vrts_per_date = dates_dict[date]
    #     # Order Products here!! QA as last
    #     # print(vrts_per_date)
    #     vrt_path = os.path.join(vrt_days + date + "final.vrt")

    #     single_vrt = gdal.BuildVRT(vrt_path, vrts_per_date, separate=True)

    #     tiff_path = os.path.join(dstdir + date + ".tiff")
    #     all_tif = gdal.Translate(tiff_path, single_vrt)
    #     #https://gis.stackexchange.com/questions
    #     # gdalwarp -cutline dummy_region.shp -crop_to_cutline -dstalpha 007.tiff masked.tiff --> worked
    #     #warp_options = [cropToCutline=TRUE, dstAlpha = True]
    #     #final_tif = gdal.Warp(all_tif, "path_to_shape", out_tif )

    #     # final_tif = None
    #     # single_vrt = None
