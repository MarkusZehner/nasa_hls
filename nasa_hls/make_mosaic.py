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
    Mosaics HLS datasets either all hdf in the folder (shape=None)
    or the precise outline a shape (shape="your_shape.shp")

    :param srcdir: Source directory of .hdf files downloaded via batch_download or download_tiles.
    Products can appear mixed in the dir.
    :param dstdir: Directory where the tif shall be saved
    :param bands: Choice of bands
    :param product: "S30" and "L30" provided. If both products should be mosaicked, run make_mosaic sequentially
    for either product. NO SUPPORT FOR BOTH AT ONCE.
    :param shape: A vector geometry readable by ogr/gdal drivers. If no shape is given, full mosaic is made
    :return: None
    """
    # delete folder if existed
    if os.path.exists(os.path.join(path_auxil + "mosaic")):
        shutil.rmtree(path_auxil + "mosaic")

    # error raising
    if shape is not None:
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

    # get year from selected files
    year = files[0].split(os.sep)[-1].split(".")[3][0:4]

    if len(files) == 0:
        log.exception(f"FATAL ERROR : COULD NOT DERIVE PRODUCT.")
        raise ValueError(f"Could not derive the specified product {product} from hdf-files input")

    # make list of all dates in directory
    dates_doy = []
    for line in files:
        l = line.split(".")[3][4:]
        dates_doy.append(l)

    def unique_dates(liste):
        """
        Gets the unique entries from a list. These will work the keys for indexing afterwards
        :param liste:
        :return: list of unique dates
        """
        unique_dates = []
        for x in liste:
            if x not in unique_dates:
                unique_dates.append(x)
        return unique_dates

    # make the list of unique dates
    unique_doy = unique_dates(dates_doy)

    def getBand(string):
        """
        Precondition for sorting band vrts. Full paths are parsed to can Band descriptor e.g. "01" or "QA.
        :param string:
        :return:
        """
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
                build_vrt = None  # reset vrt

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

        for n, i in enumerate(days):
            # concat tif and vrt path
            tiff_path = os.path.join(dstdir + product + "_" + year + "_" + i[0][-13:-10] + ".tif")
            vrt_path = os.path.join(vrt_days + product + "_" + year + "_" + i[0][-13:-10] + "final.vrt")
            print("Final VRT: \n", vrt_path)
            print("Outfile: \n", tiff_path, "\n")

            # print the final vrt and tiff location
            print("-"*80)
            print("")
            ps = str(n + 1) + "." + "" + "GEOTiff"
            print("\033[1m" + ps + "\033[0m")
            print("Final VRT: \n", vrt_path)
            print("Outfile: \n", tiff_path, "\n")

            # important to separate the bands to 1,2,3 [...] -QA
            options = gdal.BuildVRTOptions(separate=True)

            # build vrt of one date
            single_vrt = gdal.BuildVRT(vrt_path, i, options=options)

            # cut line raster to the shape
            if shape is not None:
                single_vrt = None  # reset vrt

                # concat cmd call
                cmd = f"gdalwarp -srcnodata -1000 -cutline {shape} {vrt_path} {tiff_path}"
                print("cmd call: \n", cmd, "\n\n")
                subprocess.call(cmd, shell=True)
            else:
                gdal.Translate(tiff_path, single_vrt)

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
                build_vrt = None  # reset vrt

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

        for n, i in enumerate(days):
            print(i[0])
            # concat tif and vrt path
            tiff_path = os.path.join(dstdir + product + "_" + year + "_" + i[0][-10:-7] + ".tif")
            print(tiff_path)
            vrt_path = os.path.join(vrt_days + product + "_" + year + "_" + i[0][-10:-7] + "final.vrt")

            # print the final vrt and tiff location
            print("-"*80)
            print("")
            ps = str(n + 1) + "." + "" + "GEOTiff"
            print("\033[1m" + ps + "\033[0m")
            print("Final VRT: \n", vrt_path)
            print("Outfile: \n", tiff_path, "\n")
            
            
            # important to separate the bands to 1,2,3 [...] -QA
            options = gdal.BuildVRTOptions(separate=True)

            # build vrt of one date
            single_vrt = gdal.BuildVRT(vrt_path, i, options=options)

            # cut line raster to the shape
            if shape is not None:
                single_vrt = None  # reset vrt

                # concat cmd call
                cmd = f"gdalwarp -srcnodata -1000 -cutline {shape} {vrt_path} {tiff_path}"
                print("cmd call: \n", cmd, "\n\n")
                subprocess.call(cmd, shell=True)
            else:
                tif = gdal.Translate(tiff_path, single_vrt)