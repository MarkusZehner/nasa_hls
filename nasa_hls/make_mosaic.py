import os
import glob
from osgeo import gdal
import subprocess
import shutil
import logging

from .download_tiles import path_auxil
from .utils import BAND_NAMES

gdal.UseExceptions()
log = logging.getLogger(__name__)

def make_mosaic(srcdir=None, dstdir=None, bands=None, product=None, shape=None):
    """
    :param srcdir:
    :param dstdir:
    :param bands:
    :param product:
    :param shape: A vector geometry readable by ogr/gdal drivers
    :return:
    """
    # delete folder if existed
    if os.path.exists(os.path.join(path_auxil + "mosaic")):
        shutil.rmtree(path_auxil + "mosaic")

    # error raising
    try:
        with open(shape) as src:
            pass
    except FileNotFoundError as exc:
        log.exception(f"FATAL ERROR : VECTOR FILE DOES NOT EXIST")
        return None

    # create folders in .auxil
    os.makedirs(os.path.join(path_auxil + "mosaic/bands/"), exist_ok=True)
    os.makedirs(os.path.join(path_auxil + "mosaic/days/"), exist_ok=True)
    os.makedirs(dstdir, exist_ok=True)
    vrt_bands = os.path.join(path_auxil + "mosaic/bands/")
    vrt_days = os.path.join(path_auxil + "mosaic/days/")
    hdf_files_list = list(glob.glob(srcdir + '*.hdf'))

    # get all hdf-files from srcdir according to the product
    # error when hdf in srcdir are not comply with HLS product
    files = []
    if product == "L30":
        for line in hdf_files_list:
            if ".L30." in line:
                files.append(line)
    elif product == "S30":
        for line in hdf_files_list:
            if ".S30." in line:
                files.append(line)
    else:
        print("Please specify a product")
        return None

    if len(files) == 0:
        log.exception(f"FATAL ERROR : COULD NOT DERIVE PRODUCT.")
        raise ValueError(f"Could not derive the specified product {product} from hdf-files input")

    # make list of all dates in directory
    dates_doy = []
    for line in files:
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

        for line in files:
            # go over all the files
            line_date = line.split(".")[3][4:]

            if key == line_date:
                # get the doy
                foo.append(line)

        dataframe_dict[key] = foo

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
            # concat tif and vrt path
            tiff_path = os.path.join(dstdir + i[0][-13:-10] + ".tif")
            vrt_path = os.path.join(vrt_days + i[0][-13:-10] + "final.vrt")
            print("VRT to be cropped by vector geometry: \n", vrt_path)
            print("Outfile: \n", tiff_path, "\n")

            # important to separate the bands to 1,2,3 [...] -QA
            options = gdal.BuildVRTOptions(separate=True)

            # build vrt of one date
            single_vrt = gdal.BuildVRT(vrt_path, i, options=options)
            single_vrt = None  # leave VRT

            # concat tif path

            # cut line raster to the shape
            cmd = "gdalwarp -srcnodata -1000 -cutline {shape} {vrt_path} {tiff_path}".format(shape=shape,
                                                                                             vrt_path=vrt_path,
                                                                                             tiff_path=tiff_path)
            print("cmd call: \n", cmd, "\n\n")
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

        # PROBLEM: Glob doesn't take the bands in sequence... So sorting later needed to restore band order
        vrts = list(glob.glob(path_auxil + "mosaic/bands/" + "*.vrt"))

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
            # concat tif and vrt path
            tiff_path = os.path.join(dstdir + i[0][-10:-7] + ".tif")
            vrt_path = os.path.join(vrt_days + i[0][-10:-7] + "final.vrt")
            print("VRT to be cropped by vector geometry: \n", vrt_path)
            print("Outfile: \n", tiff_path, "\n")

            # important to separate the bands to 1,2,3 [...] -QA
            options = gdal.BuildVRTOptions(separate=True)

            # build vrt of one date
            single_vrt = gdal.BuildVRT(vrt_path, i, options=options)
            single_vrt = None  # leave VRT

            # cut line raster to the shape
            cmd = "gdalwarp -srcnodata -1000 -cutline {shape} {vrt_path} {tiff_path}".format(shape=shape,
                                                                                             vrt_path=vrt_path,
                                                                                             tiff_path=tiff_path)
            print("cmd call: \n", cmd, "\n\n")
            subprocess.call(cmd, shell=True)
            # tif = gdal.Translate(tiff_path, single_vrt)
