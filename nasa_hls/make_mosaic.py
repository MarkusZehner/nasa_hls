import os
import glob
from osgeo import gdal
import subprocess
import shutil

from .download_tiles import path_auxil
from .utils import BAND_NAMES

gdal.UseExceptions()


def make_mosaic(srcdir=None, dstdir=None, bands=None, product="S30", shape=None):
    """
    :param srcdir:
    :param dstdir:
    :param bands:
    :param product:
    :param shape:
    :return:
    """
    # delete folder if existed
    if os.path.exists(os.path.join(path_auxil + "mosaic")):
        shutil.rmtree(path_auxil + "mosaic")

    # create folders in .auxil
    os.makedirs(os.path.join(path_auxil + "mosaic/bands/"), exist_ok=True)
    os.makedirs(os.path.join(path_auxil + "mosaic/days/"), exist_ok=True)
    vrt_bands = os.path.join(path_auxil + "mosaic/bands/")
    vrt_days = os.path.join(path_auxil + "mosaic/days/")

    # get all hdf-files
    hdf_files_list = list(glob.glob(srcdir + '*.hdf'))

    # make list of all dates in directory
    dates_doy = []
    for line in hdf_files_list:
        l = line.split(".")[3][4:]
        dates_doy.append(l)

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

    # helper function for parsing bands and sort after it
    def getBand(string):
        return string.split(".")[2][-2:]

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

    ##################
    # Landsat
    ##################

    if product == "L30":
        print("Landsat")
        # TODO: more description and sync description with Sentinel loop

        for key in dataframe_dict.keys():
            # for day
            # key is the doy, values are lists of all the hdf-files for that date

            for band in long_band_names:
                # for band

                hdf_list = dataframe_dict[key]
                hdf_file_bands = []

                for hdf_file in hdf_list:
                    filename = 'HDF4_EOS:EOS_GRID:"{0}":Grid:{1}'.format(hdf_file, band)
                    hdf_file_bands.append(filename)

                # make mosaics for each band for each date
                vrt_path = os.path.join(vrt_bands + key + band + ".vrt")
                build_vrt = gdal.BuildVRT(vrt_path, hdf_file_bands)
                build_vrt = None

        # PROBLEM: Glob doesn't take the bands in sequence... So sorting later needed to restore band order
        vrts = list(glob.glob(vrt_bands + "*.vrt"))

        # make list of list of bands for each day for band stacking
        days = []
        for i in unique_doy:
            days_unique = []
            for j in vrts:
                # get day
                day = j.split(os.sep)[-1]
                if day[0:3] == i:
                    days_unique.append(j)
            days.append(days_unique)

        # sorting bands
        for i in days:
            i.sort(key=getBand)
        # print(days)

        for i in days:
            vrt_path = os.path.join(vrt_days + i[0][-13:-10] + "final.vrt")
            options = gdal.BuildVRTOptions(separate=True)
            single_vrt = gdal.BuildVRT(vrt_path, i, options=options)
            print(vrt_path)
            # concat tif path
            tiff_path = os.path.join(dstdir + i[0][-13:-10] + ".tiff")

            # cut line raster to the shape
            cmd = "gdalwarp -srcnodata -1000 -cutline {shape} {vrt_path} {tiff_path}".format(shape=shape,
                                                                                             vrt_path=vrt_path,
                                                                                             tiff_path=tiff_path)
            subprocess.call(cmd, shell=True)
            # tif = gdal.Translate(tiff_path, single_vrt)

    ##################
    # Sentinel
    ##################

    elif product == "S30":
        print("Sentinel")
        # key is the doy, values are lists of all the hdf-files for that date
        # {"001":[HLS...hdf, HLS...hdf.. ]}

        for key in dataframe_dict.keys():
            # for day
            # ['B01', 'B02', 'B03', 'B04', 'B05', 'B07', 'B08', 'B8A', 'B10', 'B11', 'B12', 'QA']
            # print("long band names: ", long_band_names)

            for band in long_band_names:
                # for band
                # get the hdf files for that date in a list
                hdf_list = dataframe_dict[key]

                # go over all the bands and mosaic the bands
                hdf_file_bands = []
                for hdf_file in hdf_list:
                    filename = 'HDF4_EOS:EOS_GRID:"{0}":Grid:{1}'.format(hdf_file, band)
                    hdf_file_bands.append(filename)

                # print("\n".join(hdf_file_bands))
                # make mosaics for each band for each date
                vrt_path = os.path.join(path_auxil + "mosaic/bands/" + key + band + ".vrt")
                build_vrt = gdal.BuildVRT(vrt_path, hdf_file_bands)
                build_vrt = None

        # depricated??!
        # dates_dict = {date: None for date in unique_doy}

        # list of vrts
        # print("\nthe unique days are: \n", unique_doy, "\n")
        # print("now all the vrts\n")
        # PROBLEM: Glob doesn't take the bands in sequence... So sorting later needed to restore band order
        vrts = list(glob.glob(path_auxil + "mosaic/bands/" + "*.vrt"))
        # print(vrts, "\n\n")

        # make list of list of bands for each day
        days = []
        for i in unique_doy:
            days_unique = []
            for j in vrts:
                day = j.split(os.sep)[-1]
                if day[0:3] == i:
                    days_unique.append(j)
            days.append(days_unique)

        # sorting bands
        for i in days:
            i.sort(key=getBand)

        for i in days:
            vrt_path = os.path.join(vrt_days + i[0][-10:-7] + "final.vrt")
            print(vrt_path)

            options = gdal.BuildVRTOptions(separate=True)
            single_vrt = gdal.BuildVRT(vrt_path, i, options=options)

            # concat tif path
            tiff_path = os.path.join(dstdir + i[0][-10:-7] + ".tiff")
            print(tiff_path)

            # cut line raster to the shape
            cmd = "gdalwarp -srcnodata -1000 -cutline {shape} {vrt_path} " \
                  "{tiff_path}".format(shape=shape, vrt_path=vrt_path, tiff_path=tiff_path)
            subprocess.call(cmd, shell=True)
            # tif = gdal.Translate(tiff_path, single_vrt)
