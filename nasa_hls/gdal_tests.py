from osgeo import gdal
import numpy as np

in_path = "/home/robin/python_projects/data/nasa_hls/hdf_tiles/HLS.L30.T34JDN.2018007.v1.4.hdf"
out_path = "/home/robin/python_projects/data/nasa_hls/hdf_tiles/"

def hdf_subdataset_extraction(hdf_file, dst_dir, subdataset):
    """unpack a single subdataset from a HDF5 container and write to GeoTiff"""
    # open the dataset
    hdf_ds = gdal.Open(hdf_file, gdal.GA_ReadOnly)
    band_ds = gdal.Open(hdf_ds.GetSubDatasets()[subdataset][0], gdal.GA_ReadOnly)

    # read into numpy array
    band_array = band_ds.ReadAsArray().astype(np.int16)

    # convert no_data values
    band_array[band_array == -28672] = -32768

    # build output path
    band_path = os.path.join(dst_dir, os.path.basename(os.path.splitext(hdf_file)[0]) + "-sd" + str(subdataset+1) + ".tif")

    # write raster
    out_ds = gdal.GetDriverByName('GTiff').Create(band_path,
                                                  band_ds.RasterXSize,
                                                  band_ds.RasterYSize,
                                                  1,  #Number of bands
                                                  gdal.GDT_Int16,
                                                  ['COMPRESS=LZW', 'TILED=YES'])
    out_ds.SetGeoTransform(band_ds.GetGeoTransform())
    out_ds.SetProjection(band_ds.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(band_array)
    out_ds.GetRasterBand(1).SetNoDataValue(-32768)

    out_ds = None  #close dataset to write to disc