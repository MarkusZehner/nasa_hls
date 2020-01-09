import urllib
import os
from pathlib import Path

import geopandas as gp

from nasa_hls.download_hls_dataset import download_batch


def download_kml(dst):
    """
    Download the necessary .kml-file

    :param dst: desired destination

    :return: destination of the .kml-file
    """

    path = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata') + '/'
    path_utm = path + "utm.kml"

    if not os.path.exists(path):
        os.mkdir(path)
        print("new directory made")


    if not os.path.exists(path_utm):
        src = (
            "https://hls.gsfc.nasa.gov/wp-content/uploads/2016/03/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml")
        urllib.request.urlretrieve(src, path_utm)

    return path_utm


def get_required_tiles_from_utm(path_to_utm_file = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata' + '/utm.kml'),
                                user_shape = os.path.join(os.path.expanduser('~'), 'Dokumente', 'nasa_hls', 'data' + '/dummy_region.shp')):

    """
    :param path_to_utm_file: requires the path where the Nasa's world-covering UTM.kml file is stored.
    Do this manually by calling function 'download_utm_tiles'.

    :return: list of tile name [str of 5 digits starting with two numbers] which geographically intersect the user
    shape and the UTM tiles.
    """

    path_to_utm_file = Path(path_to_utm_file)
    Path.exists(path_to_utm_file)
    path_to_user_polygon = Path(user_shape)

    # Enable fiona driver, then read kml-file
    gp.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    UTM_tiles = gp.read_file(path_to_utm_file, driver='KML')

    # if not proj is crs WGS84:
    # ändere


    # convert user_polygon into Gdf
    user_polygon = gp.GeoDataFrame.from_file(path_to_user_polygon)

    # perform intersection
    intersections = gp.sjoin(user_polygon, UTM_tiles, how="inner", op='intersects')

    # write UTM-codes in lis
    tiles = intersections["Name"].tolist()
    print(tiles)

    return tiles


def get_available_datasets_from_tiles(products=["S30"],
                                      years=[2018],
                                      user_shape=os.path.join(os.path.expanduser('~'), 'Dokumente', 'nasa_hls', 'data' + '/dummy_region.shp'),
                                      return_list = False):

    # retrieve required tiles from the function above
    tiles = get_required_tiles_from_utm(user_shape=user_shape)
    datasets = nasa_hls.get_available_datasets(products=products, years=years, tiles=tiles, return_list=False)

    # print entire row, set:
    # import pandas as pd
    # pd.set_option('display.max_colwidth', -1)

    return datasets

<<<<<<< HEAD
=======
def order_dataframe_by_date(date = "2018-01-01",
                            datasets = datasets):
    # indexing
    return dataset # which can be put to download_batch
>>>>>>> 225d565d76f490449d955790d2482fbb2369dc09


# if __name__ == "__main__":
#     get_available_datasets_from_tiles()