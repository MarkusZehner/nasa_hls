import zipfile
import requests
import geopandas as gp
import io
import os
import matplotlib.pyplot as plt
import sys


def download_hls_s2_tiles():
    """
    Docstring
    ----------------------------
    input:
    ----------------------------
    returns:
        path to shapefile with nasa hls test sites

    """

    url = "https://hls.gsfc.nasa.gov/wp-content/uploads/2018/10/hls_s2_tiles.zip"
    local_path = "ignored/test_tiles/"

    print(f"Downloading shapefile from url {url}...")
    request = requests.get(url)
    zip = zipfile.ZipFile(io.BytesIO(request.content))
    print("DONE")
    zip.extractall(path=local_path)

    path_to_test_tiles = local_path + "hls_s2_tiles.shp"

    return path_to_test_tiles

def get_tiles_from_shape(user_polygon):
    pass

def download_from_shape():
    pass

def tiles_list():
    #path_to_user_poly = os.getcwd() + "/ignored/user_shape/" + input("enter the local path to the shapefile of your
    # working area")

    path_to_user_poly = input("enter the local path to the shapefile of your working area")

    user_poly = gp.GeoDataFrame.from_file(path_to_user_poly)
    test_tiles = gp.GeoDataFrame.from_file(download_hls_s2_tiles())
    intersections= gp.sjoin(user_poly, test_tiles, how="inner", op='intersects')

    # write ids in list
    names = intersections["Name"].tolist()
    print(names)

    return names


# # Plot the data
# fig, ax = plt.subplots(figsize=(12, 8))
# user_poly.plot(alpha=.5, ax=ax)
# plt.show()
